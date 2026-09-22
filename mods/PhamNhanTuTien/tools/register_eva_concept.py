"""Register approved EVA sprite landmarks into one concept coordinate map.

This tool produces offline evidence and an unpromoted native candidate.  It
never writes the installed workspace or Steam EVA archive.
"""

from __future__ import annotations

from hashlib import sha256
import importlib.util
import json
import math
from pathlib import Path
import sys
from zipfile import ZipFile

import numpy as np
from PIL import Image, ImageDraw
from PIL import ImageFilter


TOOLS = Path(__file__).resolve().parent
MOD = TOOLS.parent
REPO = MOD.parents[1]
SOURCE = MOD / "assets/source/eva_approved"
ARTIFACT = SOURCE / "concept-registration"
LANDMARKS = ARTIFACT / "landmarks.json"
CONCEPT = SOURCE / "approved-design.png"
CANDIDATE = MOD / "tools/eva/output/eva-concept-registration-candidate.zip"
PLAN = ARTIFACT / "registration-plan.json"
REAR_SOURCE = ARTIFACT / "coherent-rear-crown-fixed.png"
REAR_HAT_SOURCE = ARTIFACT / "coherent-rear-crownless.png"
REAR_MASK_AID = ARTIFACT / "rear-semantic-mask-aid.png"
STRAND_MASK = ARTIFACT / "strand-ownership-front-profile.png"
REAR_STRAND_MASK = ARTIFACT / "strand-ownership-rear.png"
PLAYER_BASIC = Path(
    "C:/Program Files (x86)/Steam/steamapps/common/Don't Starve Together/"
    "data/anim/player_basic.zip"
)


def sha256_file(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def apply(matrix, point):
    vector = np.array((point[0], point[1], 1.0), dtype=np.float64)
    result = np.asarray(matrix, dtype=np.float64) @ vector
    return float(result[0] / result[2]), float(result[1] / result[2])


def inverse(matrix):
    return np.linalg.inv(np.asarray(matrix, dtype=np.float64))


def world_matrix(scale, translation):
    return np.array(((scale, 0.0, translation[0]),
                     (0.0, scale, translation[1]),
                     (0.0, 0.0, 1.0)), dtype=np.float64)


def element_matrix(element):
    a, b, c, d, tx, ty = element
    return np.array(((a, c, tx), (b, d, ty), (0.0, 0.0, 1.0)),
                    dtype=np.float64)


def distance(left, right):
    return math.hypot(left[0] - right[0], left[1] - right[1])


def extract_cutouts(source: Image.Image, regions, foreground_mask=None):
    """Apply polygon mattes while keeping every surviving source RGBA byte."""
    source = source.convert("RGBA")
    alpha = np.asarray(source.getchannel("A"), dtype=np.uint8)
    if foreground_mask is None:
        foreground = alpha > 0
        matte_alpha = alpha
    else:
        foreground_mask = foreground_mask.convert("L")
        if foreground_mask.size != source.size:
            raise ValueError("foreground matte dimensions differ from source")
        matte_alpha = np.asarray(foreground_mask, dtype=np.uint8)
        foreground = matte_alpha > 0
    raw_masks = {}
    for name, record in regions["parts"].items():
        mask = Image.new("1", source.size)
        polygons = record.get("include_polygons") or [record["polygon"]]
        drawer = ImageDraw.Draw(mask)
        for polygon in polygons:
            drawer.polygon([tuple(point) for point in polygon], fill=1)
        raw_masks[name] = np.asarray(mask, dtype=bool) & foreground
    coverage = np.zeros((source.height, source.width), dtype=np.uint16)
    for mask in raw_masks.values():
        coverage += mask
    overlap = int(np.count_nonzero(coverage > 1))
    assigned = np.zeros_like(alpha, dtype=bool)
    cutouts = {}
    changed_rgb = 0
    for name in regions["precedence"]:
        owned = raw_masks[name] & ~assigned
        assigned |= owned
        ys, xs = np.nonzero(owned)
        if len(xs) == 0:
            raise ValueError(f"empty cutout after precedence: {name}")
        left, top, right, bottom = xs.min(), ys.min(), xs.max() + 1, ys.max() + 1
        original = np.asarray(source, dtype=np.uint8)[top:bottom, left:right].copy()
        local = owned[top:bottom, left:right]
        original[~local] = 0
        original[:, :, 3] = np.where(
            local, matte_alpha[top:bottom, left:right], 0
        ).astype(np.uint8)
        image = Image.fromarray(original, "RGBA")
        source_pixels = np.asarray(source, dtype=np.uint8)[top:bottom, left:right]
        visible = original[:, :, 3] > 0
        changed_rgb += int(np.count_nonzero(
            original[:, :, :3][visible] != source_pixels[:, :, :3][visible]
        ))
        cutouts[name] = {"image": image, "origin": (int(left), int(top))}
    audit = {
        "overlap_pixels_before_precedence": overlap,
        "unassigned_visible_pixels": int(np.count_nonzero(foreground & ~assigned)),
        "changed_rgb_pixels": changed_rgb,
    }
    return cutouts, audit


def semantic_foreground_matte(mask_aid: Image.Image, source_size):
    aid = mask_aid.convert("RGB")
    if aid.size == (source_size[0] + 1, source_size[1]):
        aid = aid.crop((0, 0, source_size[0], source_size[1]))
    if aid.size != tuple(source_size):
        raise ValueError(f"semantic mask aid size {aid.size} != {tuple(source_size)}")
    pixels = np.asarray(aid, dtype=np.uint8)
    strength = pixels.max(axis=2)
    # Generated aid has a black background and antialiased colored silhouette.
    # Preserve that edge alpha; RGB always comes from the approved reference.
    strength = np.where(strength >= 32, strength, 0).astype(np.uint8)
    # One-pixel edge recovery retains the approved raster's dark outer ink,
    # which a color-only semantic aid otherwise clips at hair/crown tips.
    return Image.fromarray(strength, "L").filter(ImageFilter.MaxFilter(3))


def _polygon_array(size, polygons):
    mask = Image.new("1", size)
    draw = ImageDraw.Draw(mask)
    for polygon in polygons:
        draw.polygon([tuple(point) for point in polygon], fill=1)
    return np.asarray(mask, dtype=bool)


def _shift_labels(labels, dy, dx):
    """Shift an integer label plane without np.roll wraparound."""
    shifted = np.zeros_like(labels)
    source_y = slice(max(0, -dy), labels.shape[0] - max(0, dy))
    source_x = slice(max(0, -dx), labels.shape[1] - max(0, dx))
    target_y = slice(max(0, dy), labels.shape[0] - max(0, -dy))
    target_x = slice(max(0, dx), labels.shape[1] - max(0, -dx))
    shifted[target_y, target_x] = labels[source_y, source_x]
    return shifted


def _dilate_bool(mask, radius):
    """Fast square binary dilation using an integral image."""
    if radius <= 0:
        return np.asarray(mask, dtype=bool).copy()
    padded = np.pad(np.asarray(mask, dtype=np.uint8), radius)
    integral = np.pad(padded, ((1, 0), (1, 0))).cumsum(0).cumsum(1)
    width = 2 * radius + 1
    window = (integral[width:, width:] - integral[:-width, width:]
              - integral[width:, :-width] + integral[:-width, :-width])
    return window > 0


def build_coherent_rear_cutouts():
    """Split the coherent rear painting while retaining its source pixels.

    The generated semantic image owns no artwork: it only seeds ownership.
    Dark internal ink is assigned to the nearest adjacent semantic region.
    """
    source = Image.open(REAR_SOURCE).convert("RGBA")
    hat_source = Image.open(REAR_HAT_SOURCE).convert("RGBA")
    aid = Image.open(REAR_MASK_AID).convert("RGB")
    strand_aid = Image.open(REAR_STRAND_MASK).convert("RGB")
    if (source.size != (1143, 1376) or aid.size != source.size
            or strand_aid.size != source.size
            or hat_source.size != source.size):
        raise ValueError("unexpected coherent rear source dimensions")
    rgba = np.asarray(source, dtype=np.uint8)
    hat_rgba = np.asarray(hat_source, dtype=np.uint8)
    rgb = np.asarray(aid, dtype=np.uint8)
    alpha = rgba[:, :, 3]
    strong = alpha >= 32
    r, g, b = (rgb[:, :, index].astype(np.int16) for index in range(3))
    labels = np.zeros(alpha.shape, dtype=np.uint8)
    labels[(b > r + 40) & (b > g + 40)] = 1  # hair
    labels[(r > g + 40) & (r > b + 40)] = 2  # crown
    labels[(r > 120) & (g > 120) & (b < 100)] = 3  # gown
    labels[(g > 110) & (b > 110) & (r < 110)] = 4  # left arm
    labels[(r > 110) & (b > 110) & (g < 110)] = 5  # right arm
    labels[~strong] = 0
    # Propagate ownership through black outlines and fine internal ink.
    for _ in range(96):
        missing = strong & (labels == 0)
        if not np.any(missing):
            break
        changed = False
        for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1),
                       (-1, -1), (-1, 1), (1, -1), (1, 1)):
            neighbor = _shift_labels(labels, dy, dx)
            fill = missing & (neighbor != 0)
            if np.any(fill):
                labels[fill] = neighbor[fill]
                missing &= ~fill
                changed = True
        if not changed:
            break
    # Keep source antialiasing only near the meaningful alpha>=32 silhouette.
    edge = np.asarray(
        Image.fromarray(strong.astype(np.uint8) * 255, "L").filter(
            ImageFilter.MaxFilter(9)
        ), dtype=np.uint8
    ) > 0
    ownership = (alpha > 0) & edge
    for _ in range(8):
        missing = ownership & (labels == 0)
        if not np.any(missing):
            break
        for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1),
                       (-1, -1), (-1, 1), (1, -1), (1, 1)):
            neighbor = _shift_labels(labels, dy, dx)
            fill = missing & (neighbor != 0)
            labels[fill] = neighbor[fill]
            missing &= ~fill

    strand_rgb = np.asarray(strand_aid, dtype=np.uint8)
    sr, sg, sb = (strand_rgb[:, :, index].astype(np.int16)
                  for index in range(3))
    strands = np.zeros(alpha.shape, dtype=np.uint8)
    strands[(sr > sg + 40) & (sr > sb + 40)] = 1
    strands[(sb > sr + 40) & (sb > sg + 40)] = 2
    strands[(sg > sr + 40) & (sg > sb + 40)] = 3
    hair_domain = ownership & ((labels == 1) | (labels == 2))
    strands[~hair_domain] = 0
    for _ in range(96):
        missing = hair_domain & (strands == 0)
        if not np.any(missing):
            break
        changed = False
        for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1),
                       (-1, -1), (-1, 1), (1, -1), (1, 1)):
            neighbor = _shift_labels(strands, dy, dx)
            fill = missing & (neighbor != 0)
            if np.any(fill):
                strands[fill] = neighbor[fill]
                missing &= ~fill
                changed = True
        if not changed:
            break
    # Generated masks may leave tiny disconnected antialias islands. Preserve
    # them with a deterministic semantic fallback; the substantive connected
    # strands above always follow the reviewed ownership mask.
    isolated = hair_domain & (strands == 0)
    if np.any(isolated):
        _, isolated_x = np.indices(alpha.shape)
        strands[isolated & (labels == 2)] = 1
        strands[isolated & (labels == 1) & (isolated_x < 572)] = 2
        strands[isolated & (labels == 1) & (isolated_x >= 572)] = 3

    scale = (810.0 - 151.0) / (1273.0 - 126.0)
    tx = 417.0 - scale * 572.0
    ty = 151.0 - scale * 126.0
    source_y = lambda concept_y: (concept_y - ty) / scale
    yy, _ = np.indices(alpha.shape)
    head = strands == 1
    left_hair = strands == 2
    right_hair = strands == 3
    rear_y, rear_x = np.indices(alpha.shape)
    static_scalp = (
        ((rear_x - 572.0) / 360.0) ** 2
        + ((rear_y - 380.0) / 320.0) ** 2
    ) <= 1.0
    static_scalp &= hair_domain
    for tail in (left_hair, right_hair):
        moved = tail & ~static_scalp
        root_boundary = _dilate_bool(moved, 3) & _dilate_bool(
            tail & static_scalp, 3
        )
        root_overlap = _dilate_bool(root_boundary, 28) & tail
        tail[:] = moved | root_overlap
    # Interlocking source-strand masks still need a small hidden overlap under
    # native bone motion. Build it around their actual curved boundaries,
    # never along a rectangular x/y split.
    def expanded(mask, size):
        return _dilate_bool(mask, (size - 1) // 2)

    for left_mask, right_mask in ((left_hair, right_hair),):
        boundary = expanded(left_mask, 7) & expanded(right_mask, 7)
        band = expanded(boundary, 57) & hair_domain
        left_mask |= band
        right_mask |= band
    gown = labels == 3
    torso = gown & (yy <= source_y(650))
    skirt = gown & (yy >= source_y(570))

    def record(mask, pixels_source=rgba):
        ys, xs = np.nonzero(mask)
        if not len(xs):
            raise ValueError("empty coherent rear cutout")
        left, top, right, bottom = (
            int(xs.min()), int(ys.min()), int(xs.max() + 1), int(ys.max() + 1)
        )
        pixels = pixels_source[top:bottom, left:right].copy()
        local = mask[top:bottom, left:right]
        pixels[~local] = 0
        return {
            "image": Image.fromarray(pixels, "RGBA"),
            "origin": (left, top),
            "source_to_concept": np.array((
                (scale, 0.0, tx + scale * left),
                (0.0, scale, ty + scale * top),
                (0.0, 0.0, 1.0),
            )),
        }

    records = {
        # Normal no-hat head carries a complete source-organic rear-hair
        # undercoat. Articulated strand owners paint above it; when they move,
        # no synthetic rectangular hole can open onto the body.
        "head": record(hair_domain),
        "head_hat": record(head, hat_rgba),
        "left_hair": record(left_hair),
        "right_hair": record(right_hair),
        "torso": record(torso),
        "skirt": record(skirt),
    }
    records["audit"] = {
        "source_sha256": sha256_file(REAR_SOURCE),
        "hat_source_sha256": sha256_file(REAR_HAT_SOURCE),
        "mask_sha256": sha256_file(REAR_MASK_AID),
        "strand_mask_sha256": sha256_file(REAR_STRAND_MASK),
        "unassigned_alpha32_pixels": int(np.count_nonzero(strong & (labels == 0))),
        "scale": scale,
        "translation": [tx, ty],
        "strand_unassigned_pixels": int(np.count_nonzero(
            hair_domain & (strands == 0)
        )),
        "motion_owner": "interlocking whole-strand ownership for frames 0 and 1",
        "source_rgb_preserved": True,
    }
    return records


def refine_matte_from_source(source, matte, corrections, view):
    """Recover connected dark source ink without replacing source RGB."""
    rgba = np.asarray(source.convert("RGBA"), dtype=np.uint8)
    current = np.asarray(matte, dtype=np.uint8).copy()
    record = corrections.get(view, {})
    excludes = [item["polygon"] for item in record.get("exclude_polygons", [])]
    if excludes:
        current[_polygon_array(source.size, excludes)] = 0
    include_items = record.get("conditional_include_regions", [])
    if include_items:
        allowed = _polygon_array(
            source.size, [item["polygon"] for item in include_items]
        )
        rgb = rgba[:, :, :3].astype(np.int16)
        if view == "front":
            samples = np.concatenate((rgb[:, 100:130], rgb[:, 690:720]), axis=1)
        else:
            samples = rgb[:, 1200:1230]
        background = np.median(samples, axis=1)[:, None, :]
        contrast = np.max(np.abs(rgb - background), axis=2)
        candidates = allowed & (contrast > (9 if view == "profile" else 11))
        connected = current > 0
        # Grow only through original high-contrast pixels connected to the
        # reviewed semantic silhouette; holes/curl gaps therefore stay clear.
        for _ in range(36):
            adjacent = np.asarray(
                Image.fromarray(connected.astype(np.uint8) * 255, "L").filter(
                    ImageFilter.MaxFilter(3)
                ), dtype=np.uint8
            ) > 0
            added = candidates & adjacent & ~connected
            if not np.any(added):
                break
            connected |= added
        current[connected & allowed] = np.maximum(
            current[connected & allowed], rgba[:, :, 3][connected & allowed]
        )
    return Image.fromarray(current, "L")


def _expanded_regions(view_record):
    parts = dict(view_record["parts"])
    head = parts.pop("head_face_crown")
    outer = head["include_polygons"]
    face_polygons = [head["face_patch_for_later_expression_work"]]
    face_polygons.extend(head.get("expression_feature_seed_polygons", {}).values())
    parts["face"] = {"include_polygons": face_polygons}
    parts["crown"] = {"include_polygons": [head["crown_patch_for_later_hat_work"]]}
    parts["head_blank"] = {"include_polygons": outer}
    priority = [name for name in view_record["ownership_priority"]
                if name != "head_face_crown"]
    insert = priority.index("skirt")
    priority[insert:insert] = ["face", "crown", "head_blank"]
    return {"parts": parts, "precedence": priority}


def build_exact_cutouts(output_dir=ARTIFACT / "exact-cutouts"):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    regions = json.loads((ARTIFACT / "concept-cutout-regions.json").read_text(
        encoding="utf8"
    ))
    source = Image.open(CONCEPT).convert("RGBA")
    if list(source.size) != regions["source_size"]:
        raise ValueError("approved reference dimensions changed")
    aid = Image.open(ARTIFACT / "semantic-mask-aid.png")
    matte = semantic_foreground_matte(aid, source.size)
    corrections = json.loads((ARTIFACT / "matte-corrections.json").read_text(
        encoding="utf8"
    ))
    blank_skin = Image.open(ARTIFACT / "blank-skin-material.png").convert("RGBA")
    if blank_skin.size != source.size:
        raise ValueError("blank skin material dimensions differ from concept")
    crownless = Image.open(ARTIFACT / "crownless-blank-material.png").convert("RGBA")
    if crownless.size != source.size:
        raise ValueError("crownless material dimensions differ from concept")
    underarm_material = Image.open(
        ARTIFACT / "underarm-occlusion-plate.png"
    ).convert("RGBA")
    if underarm_material.size != source.size:
        raise ValueError("underarm material dimensions differ from concept")
    all_cutouts = {}
    audits = {}
    for view in ("front", "profile"):
        left, top, right, bottom = regions[view]["bounds"]
        view_matte = np.zeros((source.height, source.width), dtype=np.uint8)
        matte_array = np.asarray(matte, dtype=np.uint8)
        view_matte[top:bottom, left:right] = matte_array[top:bottom, left:right]
        refined = refine_matte_from_source(
            source, Image.fromarray(view_matte, "L"), corrections, view
        )
        refined_array = np.asarray(refined, dtype=np.uint8).copy()
        source_rgb = np.asarray(source, dtype=np.uint8)[:, :, :3]
        bright = source_rgb.mean(axis=2) > 100
        in_view = np.zeros_like(bright)
        in_view[top:bottom, left:right] = True
        # Semantic aids occasionally omit bright interior art. Recover those
        # source pixels before ownership assignment; the dark background in
        # the reviewed character bounds is far below this threshold.
        refined_array[bright & in_view] = 255
        refined = Image.fromarray(refined_array, "L")
        cutouts, audit = extract_cutouts(
            source, _expanded_regions(regions[view]),
            refined,
        )
        # The reviewed semantic aid contains useful anatomical ownership that
        # the coarse polygons do not: notably a curved head/back-hair seam and
        # clean arm silhouettes.  Use it only as labels; all emitted RGBA is
        # copied from the approved source.
        aid_rgb = np.asarray(aid.convert("RGB").crop(
            (0, 0, source.width, source.height)
        ), dtype=np.uint8)
        rr, gg, bb = (aid_rgb[:, :, index].astype(np.int16)
                      for index in range(3))
        semantic = np.zeros((source.height, source.width), dtype=np.uint8)
        semantic[(rr > gg + 40) & (rr > bb + 40)] = 1  # head / face / crown
        semantic[(bb > rr + 40) & (bb > gg + 40)] = 2  # back hair
        semantic[(rr > 110) & (gg > 110) & (bb < 100)] = 3  # gown
        semantic[(gg > 110) & (bb > 110) & (rr < 110)] = 4  # left / near arm
        semantic[(rr > 110) & (bb > 110) & (gg < 110)] = 5  # right / far arm
        semantic[(gg > rr + 40) & (gg > bb + 40)] = 6  # bodice
        semantic_foreground = np.asarray(refined, dtype=np.uint8) > 0
        semantic[~semantic_foreground] = 0
        for _ in range(64):
            missing = semantic_foreground & (semantic == 0)
            if not np.any(missing):
                break
            changed = False
            for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1),
                           (-1, -1), (-1, 1), (1, -1), (1, 1)):
                neighbor = _shift_labels(semantic, dy, dx)
                fill = missing & (neighbor != 0)
                if np.any(fill):
                    semantic[fill] = neighbor[fill]
                    missing &= ~fill
                    changed = True
            if not changed:
                break

        strand_rgb = np.asarray(Image.open(STRAND_MASK).convert("RGB"),
                                dtype=np.uint8)
        if strand_rgb.shape[:2] != semantic.shape:
            raise ValueError("strand ownership mask dimensions differ from concept")
        sr, sg, sb = (strand_rgb[:, :, index].astype(np.int16)
                      for index in range(3))
        strands = np.zeros(semantic.shape, dtype=np.uint8)
        strands[(sr > sg + 40) & (sr > sb + 40)] = 1  # head
        strands[(sb > sr + 40) & (sb > sg + 40)] = 2  # left/profile tail
        strands[(sg > sr + 40) & (sg > sb + 40)] = 3  # right tail
        hair_domain = ((semantic == 1) | (semantic == 2))
        strands[~hair_domain] = 0
        for _ in range(64):
            missing = hair_domain & (strands == 0)
            if not np.any(missing):
                break
            changed = False
            for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1),
                           (-1, -1), (-1, 1), (1, -1), (1, 1)):
                neighbor = _shift_labels(strands, dy, dx)
                fill = missing & (neighbor != 0)
                if np.any(fill):
                    strands[fill] = neighbor[fill]
                    missing &= ~fill
                    changed = True
            if not changed:
                break

        source_pixels = np.asarray(source, dtype=np.uint8)

        def semantic_record(mask):
            ys, xs = np.nonzero(mask)
            if not len(xs):
                raise ValueError(f"empty semantic cutout: {view}")
            box = (int(xs.min()), int(ys.min()),
                   int(xs.max() + 1), int(ys.max() + 1))
            left_, top_, right_, bottom_ = box
            pixels = source_pixels[top_:bottom_, left_:right_].copy()
            local = mask[top_:bottom_, left_:right_]
            pixels[~local] = 0
            pixels[:, :, 3] = np.where(
                local,
                np.asarray(refined, dtype=np.uint8)[top_:bottom_, left_:right_],
                0,
            ).astype(np.uint8)
            return {"image": Image.fromarray(pixels, "RGBA"),
                    "origin": (left_, top_)}

        head_record = regions[view]["parts"]["head_face_crown"]
        face_polygons = [head_record["face_patch_for_later_expression_work"]]
        face_polygons.extend(head_record.get(
            "expression_feature_seed_polygons", {}
        ).values())
        face_owner = _polygon_array(source.size, face_polygons)
        crown_owner = _polygon_array(
            source.size, [head_record["crown_patch_for_later_hat_work"]]
        )
        head_strand = strands == 1
        left_strand = strands == 2
        right_strand = strands == 3
        grid_y, grid_x = np.indices(semantic.shape)
        if view == "front":
            static_scalp = (
                ((grid_x - 418.0) / 240.0) ** 2
                + ((grid_y - 300.0) / 160.0) ** 2
            ) <= 1.0
            tails = (left_strand, right_strand)
        else:
            static_scalp = (
                ((grid_x - 1020.0) / 250.0) ** 2
                + ((grid_y - 320.0) / 190.0) ** 2
            ) <= 1.0
            tails = (left_strand,)
        static_scalp &= hair_domain
        overlap_total = np.zeros_like(head_strand)
        for tail in tails:
            moved = tail & ~static_scalp
            root_boundary = _dilate_bool(moved, 3) & _dilate_bool(
                tail & static_scalp, 3
            )
            root_overlap = _dilate_bool(root_boundary, 28) & tail
            head_strand |= (tail & static_scalp) | root_overlap
            tail[:] = moved | root_overlap
            overlap_total |= root_overlap
        audit[f"curved_{view}_root_overlap_pixels"] = int(
            np.count_nonzero(overlap_total)
        )
        left_strand &= ~face_owner & ~crown_owner
        right_strand &= ~face_owner & ~crown_owner
        hat_head_strand = head_strand.copy()
        if view == "profile":
            # The approved side art is one continuous curtain, whereas native
            # frame 2 is a small secondary lock. Keep the complete curtain on
            # the head owner; the profile-facing alias suppresses only that
            # secondary lock, while the preserved base frame remains available
            # to unrelated rear/special animations.
            head_strand |= hair_domain
        cutouts["head_blank"] = semantic_record(
            head_strand & ~face_owner & ~crown_owner
        )
        cutouts["head_hat_seed"] = semantic_record(
            hat_head_strand & ~face_owner & ~crown_owner
        )
        cutouts["back_hair"] = semantic_record(left_strand | right_strand)
        cutouts["back_hair_left"] = semantic_record(left_strand)
        if view == "front":
            cutouts["back_hair_right"] = semantic_record(right_strand)
        arm_label = {"front": {"left": 4, "right": 5},
                     "profile": {"near": 4}}[view]
        arm_names = [name for name in regions[view]["ownership_priority"]
                     if name.endswith(("upper_arm", "forearm", "hand"))]
        assigned_arm = np.zeros(semantic.shape, dtype=bool)
        profile_sleeve_panel = None
        if view == "profile":
            profile_sleeve_panel = _polygon_array(source.size, [[
                [982, 620], [975, 630], [968, 640], [960, 650],
                [950, 660], [956, 670], [964, 680], [963, 690],
                [970, 700], [976, 710], [981, 721], [991, 711],
                [998, 701], [1004, 691], [1010, 680], [1012, 668],
                [1020, 649], [1018, 637], [1005, 634], [1000, 624],
            ]]) & semantic_foreground
        for arm_name in arm_names:
            side = arm_name.split("_", 1)[0]
            polygons = regions[view]["parts"][arm_name].get(
                "include_polygons", []
            )
            polygon_mask = _polygon_array(source.size, polygons)
            candidate = (semantic == arm_label[side]) & polygon_mask
            if view == "profile" and arm_name == "near_forearm":
                # The long petal below the wrist is a gown side panel in the
                # approved silhouette. Keep only cuff/skin articulated; the
                # panel is attached to skirt below so it cannot spear outward.
                candidate &= ~profile_sleeve_panel
            owned = candidate & ~assigned_arm
            assigned_arm |= owned
            cutouts[arm_name] = semantic_record(owned)
        if profile_sleeve_panel is not None:
            panel = semantic_record(profile_sleeve_panel & ~assigned_arm)
            skirt_canvas = Image.new("RGBA", source.size)
            skirt_canvas.alpha_composite(
                cutouts["skirt"]["image"], cutouts["skirt"]["origin"]
            )
            skirt_canvas.alpha_composite(panel["image"], panel["origin"])
            skirt_box = skirt_canvas.getchannel("A").getbbox()
            cutouts["skirt"] = {
                "image": skirt_canvas.crop(skirt_box),
                "origin": skirt_box[:2],
            }
            audit["static_profile_sleeve_panel_pixels"] = int(
                np.count_nonzero(profile_sleeve_panel & ~assigned_arm)
            )

        def merge_source_patch(name, rectangle):
            patch_window = np.zeros(semantic.shape, dtype=bool)
            left_p, top_p, right_p, bottom_p = rectangle
            patch_window[top_p:bottom_p, left_p:right_p] = True
            bright_near = _dilate_bool(bright & patch_window, 2)
            patch_mask = patch_window & semantic_foreground & bright_near
            if not np.any(patch_mask):
                return 0
            patch = semantic_record(patch_mask)
            merged = Image.new("RGBA", source.size)
            merged.alpha_composite(
                cutouts[name]["image"], cutouts[name]["origin"]
            )
            merged.alpha_composite(patch["image"], patch["origin"])
            box = merged.getchannel("A").getbbox()
            cutouts[name] = {"image": merged.crop(box), "origin": box[:2]}
            return int(np.count_nonzero(patch_mask))

        if view == "front":
            audit["restored_neck_pixels"] = merge_source_patch(
                "torso", (398, 499, 432, 517)
            )
            audit["restored_bodice_pixels"] = merge_source_patch(
                "torso", (362, 565, 394, 621)
            )
            audit["restored_left_petal_pixels"] = merge_source_patch(
                "skirt", (305, 645, 352, 710)
            )
        else:
            audit["restored_profile_curl_pixels"] = merge_source_patch(
                "back_hair", (831, 637, 860, 696)
            )
            audit["restored_profile_sleeve_pixels"] = merge_source_patch(
                "skirt", (945, 690, 980, 723)
            )
            audit["restored_profile_neck_pixels"] = merge_source_patch(
                "torso", (1065, 481, 1081, 504)
            )
        audit["semantic_unassigned_pixels"] = int(np.count_nonzero(
            semantic_foreground & (semantic == 0)
        ))
        audit["strand_unassigned_pixels"] = int(np.count_nonzero(
            hair_domain & (strands == 0)
        ))
        audit["semantic_source_rgb_preserved"] = True
        # Native hair matrices move independently from the head. Keep a
        # source-exact central underlap on the static head owner; padding the
        # moving pigtail itself repeated a hard scalp edge at idle 32--35.
        head_mask = _polygon_array(source.size, head_record["include_polygons"])
        face_mask = _polygon_array(source.size, face_polygons)
        crown_mask_for_padding = _polygon_array(
            source.size, [head_record["crown_patch_for_later_hat_work"]]
        )
        # Least-squares low-slip roots measured across all 66 native idle
        # frames.  Circular, strand-local overlap avoids exposing a ruler-
        # straight crop edge while the pigtail matrices rotate independently.
        roots = ((373.08, 455.84), (470.11, 471.37)) if view == "front" else (
            (1027.44, 505.60),
        )
        underlap_image = Image.new("1", source.size)
        underlap_draw = ImageDraw.Draw(underlap_image)
        radius = 30
        for root_x, root_y in roots:
            underlap_draw.ellipse(
                (root_x - radius, root_y - radius,
                 root_x + radius, root_y + radius), fill=1,
            )
        underlap_window = np.asarray(underlap_image, dtype=bool)
        existing_hair = Image.new("RGBA", source.size)
        existing_hair.alpha_composite(cutouts["back_hair"]["image"],
                                      cutouts["back_hair"]["origin"])
        existing_hair_pixels = np.asarray(existing_hair, dtype=np.uint8)
        underlap_mask = (underlap_window
                         & (existing_hair_pixels[:, :, 3] > 0)
                         & ~face_mask & ~crown_mask_for_padding)
        head_underlap = existing_hair_pixels.copy()
        head_underlap[:, :, 3] = np.where(
            underlap_mask, head_underlap[:, :, 3], 0
        ).astype(np.uint8)
        audit["hidden_hair_padding_pixels"] = int(np.count_nonzero(underlap_mask))
        arm_names = (
            ("left_upper_arm", "right_upper_arm", "left_forearm",
             "right_forearm", "left_hand", "right_hand")
            if view == "front"
            else ("near_upper_arm", "near_forearm", "near_hand")
        )
        arm_polygons = []
        for arm_name in arm_names:
            arm_polygons.extend(
                regions[view]["parts"][arm_name].get("include_polygons", [])
            )
        arm_footprint = Image.fromarray(
            _polygon_array(source.size, arm_polygons).astype(np.uint8) * 255, "L"
        ).filter(ImageFilter.MaxFilter(11))
        plate_rgb = np.asarray(underarm_material, dtype=np.uint8)[:, :, :3]
        if view == "front":
            plate_samples = np.concatenate(
                (plate_rgb[:, 100:130], plate_rgb[:, 690:720]), axis=1
            )
        else:
            plate_samples = plate_rgb[:, 1200:1230]
        plate_background = np.median(
            plate_samples.astype(np.int16), axis=1
        )[:, None, :]
        plate_contrast = np.max(np.abs(
            plate_rgb.astype(np.int16) - plate_background
        ), axis=2)
        plate_mask = ((np.asarray(arm_footprint, dtype=np.uint8) > 0)
                      & (plate_contrast > 9))
        plate_pixels = np.asarray(underarm_material, dtype=np.uint8).copy()
        plate_pixels[:, :, 3] = np.where(
            plate_mask, plate_pixels[:, :, 3], 0
        ).astype(np.uint8)
        if view == "front":
            split = 418
            x_grid = np.indices(plate_mask.shape)[1]
            for name, side_mask in (
                    ("back_hair_left", x_grid <= split),
                    ("back_hair_right", x_grid >= split)):
                side_plate = plate_pixels.copy()
                side_plate[:, :, 3] = np.where(
                    side_mask, side_plate[:, :, 3], 0
                ).astype(np.uint8)
                combined = Image.fromarray(side_plate, "RGBA")
                combined.alpha_composite(
                    cutouts[name]["image"], cutouts[name]["origin"]
                )
                box = combined.getchannel("A").getbbox()
                cutouts[name] = {
                    "image": combined.crop(box), "origin": box[:2],
                }
        else:
            backing = Image.fromarray(plate_pixels, "RGBA")
            backing_box = backing.getchannel("A").getbbox()
            cutouts["underarm_backing"] = {
                "image": backing.crop(backing_box), "origin": backing_box[:2],
            }
        # Hidden restoration belongs to the back-hair depth branch.  Putting
        # it on torso paints over the articulated arms in native Z order.
        hair_with_plate = Image.fromarray(plate_pixels, "RGBA")
        hair_with_plate.alpha_composite(
            cutouts["back_hair"]["image"], cutouts["back_hair"]["origin"]
        )
        hair_plate_box = hair_with_plate.getchannel("A").getbbox()
        cutouts["back_hair"] = {
            "image": hair_with_plate.crop(hair_plate_box),
            "origin": hair_plate_box[:2],
        }
        cutouts["torso_with_underarm"] = {
            "image": cutouts["torso"]["image"],
            "origin": cutouts["torso"]["origin"],
        }
        audit["hidden_underarm_plate_pixels"] = int(np.count_nonzero(plate_mask))
        head = Image.fromarray(head_underlap, "RGBA")
        head.alpha_composite(cutouts["head_blank"]["image"],
                             cutouts["head_blank"]["origin"])
        face_alpha = Image.new("L", source.size)
        face_alpha.paste(cutouts["face"]["image"].getchannel("A"),
                         cutouts["face"]["origin"])
        generated_skin = blank_skin.copy()
        generated_skin.putalpha(face_alpha)
        head.alpha_composite(generated_skin)
        crown_alpha = Image.new("L", source.size)
        crown_alpha.paste(cutouts["crown"]["image"].getchannel("A"),
                          cutouts["crown"]["origin"])
        crownless_rgb = np.asarray(crownless, dtype=np.uint8)[:, :, :3]
        if view == "front":
            background_samples = np.concatenate(
                (crownless_rgb[:, 100:130], crownless_rgb[:, 690:720]), axis=1
            )
        else:
            background_samples = crownless_rgb[:, 1200:1230]
        crownless_background = np.median(
            background_samples.astype(np.int16), axis=1
        )[:, None, :]
        crownless_contrast = np.max(np.abs(
            crownless_rgb.astype(np.int16) - crownless_background
        ), axis=2)
        crownless_hair = (
            crownless_rgb[:, :, 2].astype(np.int16)
            >= crownless_rgb[:, :, 0].astype(np.int16) - 18
        )
        crown_fill_mask = ((np.asarray(crown_alpha, dtype=np.uint8) > 0)
                           & (crownless_contrast > 11) & crownless_hair)
        crown_fill = np.asarray(crownless, dtype=np.uint8).copy()
        crown_fill[:, :, 3] = np.where(
            crown_fill_mask, crown_fill[:, :, 3], 0
        ).astype(np.uint8)
        hat_head = Image.fromarray(head_underlap, "RGBA")
        hat_head.alpha_composite(cutouts["head_hat_seed"]["image"],
                                 cutouts["head_hat_seed"]["origin"])
        hat_head.alpha_composite(generated_skin)
        hat_head.alpha_composite(Image.fromarray(crown_fill, "RGBA"))
        hat_box = hat_head.getchannel("A").getbbox()
        cutouts["head_hat_blank"] = {
            "image": hat_head.crop(hat_box), "origin": hat_box[:2],
        }
        head.alpha_composite(Image.fromarray(crown_fill, "RGBA"))
        head_alpha = head.getchannel("A").getbbox()
        cutouts["head_blank"] = {
            "image": head.crop(head_alpha), "origin": head_alpha[:2],
        }
        crowned = head.copy()
        crowned.alpha_composite(cutouts["crown"]["image"],
                                cutouts["crown"]["origin"])
        crowned_box = crowned.getchannel("A").getbbox()
        cutouts["head_with_crown"] = {
            "image": crowned.crop(crowned_box), "origin": crowned_box[:2],
        }
        audit["blank_skin_generated_pixels"] = int(np.count_nonzero(
            np.asarray(face_alpha, dtype=np.uint8)
        ))
        audit["crownless_hidden_hair_pixels"] = int(np.count_nonzero(
            crown_fill_mask
        ))
        reconstruction = Image.new("RGBA", source.size)
        for name, record in cutouts.items():
            path = output_dir / f"{view}-{name}.png"
            record["image"].save(path)
            record["path"] = path
        render_order = [name for name in cutouts
                        if name not in {"head_blank", "head_with_crown",
                                        "torso_with_underarm",
                                        "crown", "face"}]
        render_order.extend(("head_blank", "crown", "face"))
        for name in render_order:
            record = cutouts[name]
            reconstruction.alpha_composite(record["image"], record["origin"])
        reconstruction.save(output_dir / f"{view}-reconstruction.png")
        all_cutouts[view] = cutouts
        audits[view] = audit
    return all_cutouts, audits


def fit_affine(source, target):
    if len(source) < 3 or len(source) != len(target):
        raise ValueError("affine fit needs at least three paired landmarks")
    design = []
    values = []
    for (x, y), (u, v) in zip(source, target):
        design.extend(((x, y, 1, 0, 0, 0), (0, 0, 0, x, y, 1)))
        values.extend((u, v))
    coefficients, *_ = np.linalg.lstsq(
        np.asarray(design, dtype=np.float64),
        np.asarray(values, dtype=np.float64),
        rcond=None,
    )
    return np.array(((coefficients[0], coefficients[1], coefficients[2]),
                     (coefficients[3], coefficients[4], coefficients[5]),
                     (0.0, 0.0, 1.0)), dtype=np.float64)


def fit_similarity(source, target):
    if len(source) != 2 or len(target) != 2:
        raise ValueError("oriented similarity fit needs two paired landmarks")
    (x0, y0), (x1, y1) = source
    (u0, v0), (u1, v1) = target
    source_delta = complex(x1 - x0, y1 - y0)
    target_delta = complex(u1 - u0, v1 - v0)
    if abs(source_delta) < 1e-9:
        raise ValueError("coincident source landmarks")
    factor = target_delta / source_delta
    translation = complex(u0, v0) - factor * complex(x0, y0)
    return np.array(((factor.real, -factor.imag, translation.real),
                     (factor.imag, factor.real, translation.imag),
                     (0.0, 0.0, 1.0)), dtype=np.float64)


def _load_builder():
    path = TOOLS / "build_eva_approved.py"
    spec = importlib.util.spec_from_file_location("eva_approved_builder", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _fit_part(record, target_variant=None, part_name=None):
    anchors = record["anchors"]
    target_key = f"targets_{target_variant}" if target_variant else "targets"
    targets = record[target_key]
    shared = [name for name in anchors if name in targets]
    if part_name == "forearm":
        shared = ["elbow", "wrist"]
    elif part_name == "face" and "left_eye" in anchors:
        shared = ["left_eye", "right_eye", "mouth"]
    if len(shared) == 2:
        return fit_similarity([anchors[name] for name in shared],
                              [targets[name] for name in shared])
    return fit_affine([anchors[name] for name in shared],
                      [targets[name] for name in shared])


def _warp(image, matrix, size):
    inv = inverse(matrix)
    coefficients = (inv[0, 0], inv[0, 1], inv[0, 2],
                    inv[1, 0], inv[1, 1], inv[1, 2])
    return image.transform(size, Image.Transform.AFFINE, coefficients,
                           Image.Resampling.BICUBIC)


def _render_view(view, parts, specification):
    size = tuple(specification["reference_size"])
    canvas = Image.new("RGBA", size)
    records = specification["source_parts"][view]
    residuals = []
    layers = []

    def put(name, image=None, variant=None, mirror=False):
        source = image if image is not None else parts[view][name]
        record = records[name]
        matrix = _fit_part(record, variant, name)
        if mirror:
            source = source.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
            reflect = np.array(((-1.0, 0.0, record["size"][0] - 1.0),
                                (0.0, 1.0, 0.0), (0.0, 0.0, 1.0)))
            matrix = matrix @ reflect
        warped = _warp(source, matrix, size)
        canvas.alpha_composite(warped)
        layers.append((f"{name}_{variant}" if variant else name, warped))
        target_key = f"targets_{variant}" if variant else "targets"
        for anchor_name, target in record[target_key].items():
            original = record["anchors"].get(anchor_name)
            if original is None:
                continue
            if mirror:
                original = (record["size"][0] - 1 - original[0], original[1])
            actual = apply(matrix, original)
            residuals.append({
                "part": name, "anchor": anchor_name,
                "target": target, "actual": actual,
                "error": distance(actual, target),
            })

    put("back_hair")
    put("skirt")
    put("bodice")
    if view == "front":
        put("upper_arm", variant="left")
        put("forearm", variant="left")
        put("hand", variant="left")
        put("upper_arm", variant="right", mirror=True)
        put("forearm", variant="right", mirror=True)
        put("hand", variant="right", mirror=True)
    else:
        put("upper_arm")
        put("forearm")
        put("hand")
    put("head_blank")
    put("face")
    put("crown")
    return canvas, residuals, layers


def _quad_corners(image, source_to_concept, concept_to_world, element,
                  source_rect=None):
    if source_rect is None:
        source_rect = (0, 0, image.width, image.height)
    left, top, right, bottom = source_rect
    source_to_build = inverse(element) @ concept_to_world @ source_to_concept
    return [apply(source_to_build, point) for point in (
        (left, top), (right, top), (left, bottom), (right, bottom),
    )]


def _elements(builder, rows, symbol, frame):
    key = builder.sdbm(symbol)
    return [row for row in rows if row[0] == key and row[1] == frame]


def _load_player_clip(builder, archive_path, name, facing):
    """Read one exact native clip without importing the preview renderer."""
    with ZipFile(archive_path) as archive:
        reader = builder.Reader(archive.read("anim.bin"))
    magic, version, _, _, _, clip_count = reader.unpack("4sIIIII")
    if (magic, version) != (b"ANIM", 4):
        raise ValueError("expected ANIM v4")
    match = None
    for _ in range(clip_count):
        clip_name = reader.string()
        clip_facing, _, _, frame_count = reader.unpack("BIfI")
        frames = []
        for _ in range(frame_count):
            reader.take(16)
            reader.take(reader.uint() * 4)
            frames.append([
                builder.ELEMENT.unpack(reader.take(builder.ELEMENT.size))
                for _ in range(reader.uint())
            ])
        if clip_name == name and clip_facing == facing:
            if match is not None:
                raise ValueError(f"duplicate native clip {name!r}/{facing}")
            match = frames
    if match is None:
        raise ValueError(f"native clip missing: {name!r}/{facing}")
    return match


def _front_run_limb_groups(builder, frames):
    """Pair the two visible upper-0 run chains by their authored order."""
    upper_hash = builder.sdbm("arm_upper")
    lower_hash = builder.sdbm("arm_lower")
    hand_hash = builder.sdbm("hand")
    expected = {(2, 5), (1, 2)}
    groups = {key: [] for key in expected}
    for frame_index, elements in enumerate(frames):
        upper_positions = [
            index for index, row in enumerate(elements)
            if row[0] == upper_hash and row[1] == 0
        ]
        seen = set()
        for upper_position in upper_positions:
            hand_candidates = [
                (index, row) for index, row in enumerate(elements[:upper_position])
                if row[0] == hand_hash and row[1] in (2, 5)
                and index not in seen
            ]
            lower_candidates = [
                (index, row) for index, row in enumerate(elements[upper_position + 1:],
                                                         upper_position + 1)
                if row[0] == lower_hash and row[1] in (1, 2)
            ]
            if not hand_candidates or not lower_candidates:
                continue
            hand_position, hand = max(hand_candidates, key=lambda item: item[0])
            lower_position, lower = min(lower_candidates, key=lambda item: item[0])
            pair = (lower[1], hand[1])
            if pair not in expected:
                continue
            seen.add(hand_position)
            groups[pair].append({
                "animation_frame": frame_index,
                "upper": element_matrix(elements[upper_position][3:9]),
                "lower": element_matrix(lower[3:9]),
                "hand": element_matrix(hand[3:9]),
            })
        if sum(row["animation_frame"] == frame_index
               for rows in groups.values() for row in rows) != 2:
            raise ValueError(f"front run frame {frame_index} limb grouping changed")
    if any(len(rows) != len(frames) for rows in groups.values()):
        raise ValueError("front run limb pair coverage changed")
    return groups


def _fit_front_run_chain(groups, upper_elbow):
    """Fit static local elbow/wrist anchors against all native run matrices."""
    result = {}
    upper_point = np.asarray(upper_elbow, dtype=np.float64)
    for (lower_frame, hand_frame), rows in groups.items():
        elbow_design = []
        elbow_values = []
        for row in rows:
            upper = row["upper"]
            lower = row["lower"]
            elbow_design.append(lower[:2, :2])
            elbow_values.append(
                upper[:2, :2] @ upper_point + upper[:2, 2] - lower[:2, 2]
            )
        lower_elbow, *_ = np.linalg.lstsq(
            np.vstack(elbow_design), np.concatenate(elbow_values), rcond=None
        )

        joint_design = []
        joint_values = []
        for row in rows:
            lower = row["lower"]
            hand = row["hand"]
            joint_design.append(np.hstack((lower[:2, :2], -hand[:2, :2])))
            joint_values.append(hand[:2, 2] - lower[:2, 2])
        fitted, *_ = np.linalg.lstsq(
            np.vstack(joint_design), np.concatenate(joint_values), rcond=None
        )
        lower_wrist = fitted[:2]
        hand_wrist = fitted[2:]

        elbow_errors = []
        wrist_errors = []
        for row in rows:
            upper = row["upper"]
            lower = row["lower"]
            hand = row["hand"]
            upper_world = upper[:2, :2] @ upper_point + upper[:2, 2]
            lower_elbow_world = lower[:2, :2] @ lower_elbow + lower[:2, 2]
            lower_wrist_world = lower[:2, :2] @ lower_wrist + lower[:2, 2]
            hand_world = hand[:2, :2] @ hand_wrist + hand[:2, 2]
            elbow_errors.append(float(np.linalg.norm(upper_world - lower_elbow_world)))
            wrist_errors.append(float(np.linalg.norm(lower_wrist_world - hand_world)))
        result[(lower_frame, hand_frame)] = {
            "lower_elbow": tuple(map(float, lower_elbow)),
            "lower_wrist": tuple(map(float, lower_wrist)),
            "hand_wrist": tuple(map(float, hand_wrist)),
            "max_elbow_error_native": max(elbow_errors),
            "max_wrist_error_native": max(wrist_errors),
            "rms_elbow_error_native": math.sqrt(
                sum(value * value for value in elbow_errors) / len(elbow_errors)
            ),
            "rms_wrist_error_native": math.sqrt(
                sum(value * value for value in wrist_errors) / len(wrist_errors)
            ),
        }
    return result


def _corners_from_affine(image, matrix):
    return [apply(matrix, point) for point in (
        (0, 0), (image.width, 0), (0, image.height),
        (image.width, image.height),
    )]


def _split_forearm_joint_and_pendant(record, anchors, radius=20.0):
    """Partition exact forearm pixels into articulated cuff and gown pendant."""
    pixels = np.asarray(record["image"].convert("RGBA"), dtype=np.uint8)
    height, width = pixels.shape[:2]
    ox, oy = record["origin"]
    yy, xx = np.mgrid[0:height, 0:width]
    points_x = xx + ox
    points_y = yy + oy
    elbow = np.asarray(anchors["elbow"], dtype=np.float64)
    wrist = np.asarray(anchors["wrist"], dtype=np.float64)
    vector = wrist - elbow
    length_squared = float(vector @ vector)
    projection = (
        (points_x - elbow[0]) * vector[0]
        + (points_y - elbow[1]) * vector[1]
    ) / length_squared
    projection_clamped = np.clip(projection, -0.30, 1.30)
    nearest_x = elbow[0] + projection_clamped * vector[0]
    nearest_y = elbow[1] + projection_clamped * vector[1]
    distance_to_bone = np.hypot(points_x - nearest_x, points_y - nearest_y)
    foreground = pixels[:, :, 3] > 0
    joint_mask = foreground & (distance_to_bone <= radius)
    pendant_mask = foreground & ~joint_mask
    if not np.any(joint_mask) or not np.any(pendant_mask):
        raise ValueError("forearm joint/pendant partition is empty")

    def masked(mask):
        image = pixels.copy()
        image[~mask] = 0
        return {"image": Image.fromarray(image, "RGBA"), "origin": record["origin"]}

    return masked(joint_mask), masked(pendant_mask), {
        "foreground_pixels": int(np.count_nonzero(foreground)),
        "joint_pixels": int(np.count_nonzero(joint_mask)),
        "pendant_pixels": int(np.count_nonzero(pendant_mask)),
        "union_exact": bool(np.array_equal(joint_mask | pendant_mask, foreground)),
        "overlap_pixels": int(np.count_nonzero(joint_mask & pendant_mask)),
        "radius_concept_pixels": radius,
    }


def _fit_segment_with_fixed_width(source, target, source_to_neutral_local):
    """Fit endpoints exactly while retaining neutral cross-bone pixel scale."""
    source_start = np.asarray(source[0], dtype=np.float64)
    source_end = np.asarray(source[1], dtype=np.float64)
    target_start = np.asarray(target[0], dtype=np.float64)
    target_end = np.asarray(target[1], dtype=np.float64)
    source_vector = source_end - source_start
    source_length = float(np.linalg.norm(source_vector))
    if source_length < 1e-9:
        raise ValueError("coincident forearm anchors")
    source_perpendicular = np.array(
        (-source_vector[1], source_vector[0]), dtype=np.float64
    ) / source_length
    neutral_perpendicular = (
        np.asarray(source_to_neutral_local, dtype=np.float64)[:2, :2]
        @ source_perpendicular
    )
    target_vector = target_end - target_start
    target_length = float(np.linalg.norm(target_vector))
    if target_length < 1e-9:
        raise ValueError("coincident fitted forearm anchors")
    target_perpendicular = np.array(
        (-target_vector[1], target_vector[0]), dtype=np.float64
    ) / target_length
    # Preserve handedness from the neutral mapping while keeping its width.
    # Comparing perpendicular directions is wrong across >90-degree rotations:
    # it can turn a 180-degree rotation into a reflection.  The determinant is
    # the invariant that distinguishes those cases.
    if float(np.linalg.det(
        np.asarray(source_to_neutral_local, dtype=np.float64)[:2, :2]
    )) < 0:
        target_perpendicular *= -1
    target_perpendicular *= float(np.linalg.norm(neutral_perpendicular))
    return fit_affine(
        [source_start, source_end, source_start + source_perpendicular],
        [target_start, target_end, target_start + target_perpendicular],
    )


def build_registered_candidate(output=CANDIDATE, plan_path=PLAN):
    builder = _load_builder()
    specification = json.loads(LANDMARKS.read_text(encoding="utf8"))
    regions = json.loads((ARTIFACT / "concept-cutout-regions.json").read_text(
        encoding="utf8"
    ))
    cutouts, cutout_audit = build_exact_cutouts()
    front_forearm_partition = {}
    for name in ("left_forearm", "right_forearm"):
        joint, pendant, audit = _split_forearm_joint_and_pendant(
            cutouts["front"][name],
            regions["front"]["parts"][name]["anchors"],
        )
        cutouts["front"][f"{name}_joint"] = joint
        cutouts["front"][f"{name}_pendant"] = pendant
        front_forearm_partition[name] = audit
    rear_cutouts = build_coherent_rear_cutouts()
    scale = specification["world_map"]["scale"]
    world = {
        "front": world_matrix(scale, specification["world_map"]["front_translation"]),
        "profile": world_matrix(scale, specification["world_map"]["profile_translation"]),
        # Rear authored art occupies the same concept silhouette as front.
        # Register it through the same concept->native map; identity here
        # would leave it hundreds of native pixels away from legacy limbs.
        "rear": world_matrix(scale, specification["world_map"]["front_translation"]),
    }
    idles = {
        "front": builder.load_idle(8)[8],
        "profile": builder.load_idle(5)[8],
        "rear": builder.load_idle(2)[8],
    }
    overrides = {}
    binding_rows = []

    def registered_spec(view, pieces, source):
        emitted = []
        for piece in pieces:
            image = piece["image"]
            matrix = piece["matrix"]
            element = piece["element"]
            rect = piece.get("source_rect")
            emitted.append({
                "image": image,
                "corners": _quad_corners(
                    piece.get("full_image", image), matrix, world[view], element, rect
                ),
            })
        return {"pieces": emitted, "source": source}

    def add_override(symbol, frame, view, pieces, source):
        overrides[(symbol, frame)] = registered_spec(view, pieces, source)

    def first_element(view, symbol, frame, sort_x=False, ordinal=0):
        found = _elements(builder, idles[view], symbol, frame)
        if not found:
            raise ValueError(f"idle8 lacks {view} {symbol}:{frame}")
        if sort_x:
            found.sort(key=lambda row: row[7])
        if ordinal >= len(found):
            raise ValueError(f"idle8 lacks {view} {symbol}:{frame} element {ordinal}")
        return element_matrix(found[ordinal][3:9])

    def part_piece(view, name, element, source_rect=None):
        record = cutouts[view][name]
        ox, oy = record["origin"]
        return {
            "image": record["image"] if source_rect is None
                     else record["image"].crop(source_rect),
            "full_image": record["image"],
            "source_rect": source_rect,
            # Exact-raster parts already live in the common concept map.
            # Only their crop origin is restored; no scale/shear is fitted.
            "matrix": np.array(((1.0, 0.0, ox),
                                (0.0, 1.0, oy),
                                (0.0, 0.0, 1.0))),
            "element": element,
        }

    def coherent_rear_piece(name, element):
        record = rear_cutouts[name]
        return {
            "image": record["image"],
            "matrix": record["source_to_concept"],
            "element": element,
        }

    front_head = first_element("front", "headbase", 0)
    profile_head = first_element("profile", "headbase", 1)
    add_override("headbase", 0, "front", [
        part_piece("front", "head_with_crown", front_head),
    ], "approved_design#concept_registered_front_head")
    add_override("headbase_hat", 0, "front", [
        part_piece("front", "head_hat_blank", front_head),
    ], "crownless_material#concept_registered_front_head_hat")
    add_override("headbase", 1, "profile", [
        part_piece("profile", "head_with_crown", profile_head),
    ], "approved_design#concept_registered_profile_head")
    add_override("headbase_hat", 1, "profile", [
        part_piece("profile", "head_hat_blank", profile_head),
    ], "crownless_material#concept_registered_profile_head_hat")
    rear_head = first_element("rear", "headbase", 2)
    add_override("headbase", 2, "rear", [coherent_rear_piece(
        "head", rear_head
    )], "coherent_rear#uniform_registered_head")
    add_override("headbase_hat", 2, "rear", [coherent_rear_piece(
        "head_hat", rear_head
    )], "coherent_rear_hat#crown_omitted_hat_head")

    add_override("face", 0, "front", [part_piece(
        "front", "face", first_element("front", "face", 0)
    )], "approved_design#concept_registered_front_face")
    add_override("face", 4, "profile", [part_piece(
        "profile", "face", first_element("profile", "face", 4)
    )], "approved_design#concept_registered_profile_face")
    add_override("face", 33, "front", [part_piece(
        "front", "face", first_element("front", "face", 0)
    )], "approved_design#exact_front_neutral_fallback")

    # Retained donor expressions must occupy the same newly registered face
    # space as the exact neutral cutout.  A single local transform per facing
    # preserves expression motion; frame 14 is the skeleton/shock branch and
    # deliberately keeps its special geometry.
    # Feature-based fits use donor eye/mouth landmarks rather than transparent
    # face-quad margins. C maps donor local face geometry into concept pixels;
    # inverse(element) then registers it into the native build coordinate space.
    front_face_to_concept = np.array((
        (1.527001, -0.103800, 431.921824),
        (-0.013238, 1.464917, 404.514659),
        (0.0, 0.0, 1.0),
    ))
    profile_face_to_concept = np.array((
        (1.407820, 0.159919, 1128.072532),
        (-0.159919, 1.407820, 395.110691),
        (0.0, 0.0, 1.0),
    ))
    front_expression_transform = (
        inverse(first_element("front", "face", 0))
        @ world["front"] @ front_face_to_concept
    )
    profile_expression_transform = (
        inverse(first_element("profile", "face", 4))
        @ world["profile"] @ profile_face_to_concept
    )
    registration_geometry = {}
    for index in list(range(1, 4)) + list(range(8, 14)) + list(range(15, 33)):
        registration_geometry[("face", index)] = front_expression_transform
    for index in range(5, 8):
        registration_geometry[("face", index)] = profile_expression_transform
    add_override("torso", 0, "front", [part_piece(
        "front", "torso_with_underarm", first_element("front", "torso", 0)
    )], "approved_design#concept_registered_front_bodice")
    add_override("torso", 3, "profile", [part_piece(
        "profile", "torso_with_underarm", first_element("profile", "torso", 3)
    )], "approved_design#concept_registered_profile_bodice")
    add_override("torso", 6, "rear", [coherent_rear_piece(
        "torso", first_element("rear", "torso", 6)
    )], "coherent_rear#uniform_registered_bodice")
    front_skirt_element = first_element("front", "skirt", 0)
    add_override("skirt", 0, "front", [
        part_piece("front", "skirt", front_skirt_element),
        part_piece("front", "left_forearm_pendant", front_skirt_element),
        part_piece("front", "right_forearm_pendant", front_skirt_element),
    ], "approved_design#front_skirt_with_static_exact_sleeve_pendants")
    add_override("skirt", 1, "rear", [coherent_rear_piece(
        "skirt", first_element("rear", "skirt", 1)
    )], "coherent_rear#uniform_registered_skirt")

    front_upper = first_element("front", "arm_upper", 0, True)
    front_lower = first_element("front", "arm_lower", 0, True)
    front_hand = first_element("front", "hand", 0, True)
    add_override("arm_upper", 0, "front", [part_piece(
        "front", "left_upper_arm", front_upper
    )], "approved_design#concept_registered_left_upper_shared")
    add_override("arm_lower", 0, "front", [part_piece(
        "front", "left_forearm_joint", front_lower
    )], "approved_design#concept_registered_left_forearm_joint_shared")
    front_hand_piece = part_piece("front", "left_hand", front_hand)
    front_hand_spec = registered_spec(
        "front", [front_hand_piece],
        "approved_design#concept_registered_bilateral_hand_compromise",
    )
    right_hand_element = first_element("front", "hand", 0, True, 1)
    left_wrist = regions["front"]["parts"]["left_hand"]["anchors"]["wrist"]
    right_wrist = regions["front"]["parts"]["right_hand"]["anchors"]["wrist"]
    local_wrist = apply(inverse(front_hand) @ world["front"], left_wrist)
    current_right = apply(inverse(world["front"]) @ right_hand_element, local_wrist)
    left_linear = (inverse(world["front"]) @ front_hand)[:2, :2]
    right_linear = (inverse(world["front"]) @ right_hand_element)[:2, :2]
    design = np.vstack((left_linear, right_linear))
    values = np.array((0.0, 0.0,
                       right_wrist[0] - current_right[0],
                       right_wrist[1] - current_right[1]))
    hand_delta, *_ = np.linalg.lstsq(design, values, rcond=None)
    for piece in front_hand_spec["pieces"]:
        piece["corners"] = [
            (point[0] + hand_delta[0], point[1] + hand_delta[1])
            for point in piece["corners"]
        ]
    overrides[("hand", 0)] = front_hand_spec
    add_override("arm_upper", 2, "profile", [part_piece(
        "profile", "near_upper_arm", first_element("profile", "arm_upper", 2, True)
    )], "approved_design#concept_registered_profile_near_upper")
    add_override("hand", 2, "profile", [part_piece(
        "profile", "near_hand", first_element("profile", "hand", 2, True)
    )], "approved_design#concept_registered_profile_near_hand")

    # Whole strands are assigned by the ownership aid; never bisect a curl
    # with a vertical rectangle through the concept centerline.
    for frame, name in ((0, "back_hair_left"),
                        (1, "back_hair_right")):
        element = first_element("front", "hairpigtails", frame)
        add_override("hairpigtails", frame, "front", [part_piece(
            "front", name, element
        )], f"approved_design#concept_registered_front_back_hair_{frame}")
    rear_hair_alias_frames = {}
    for frame, name in ((0, "left_hair"), (1, "right_hair")):
        rear_hair_alias_frames[frame] = registered_spec(
            "rear", [coherent_rear_piece(
                name, first_element("rear", "hairpigtails", frame)
            )], f"coherent_rear#whole_strand_owner_{frame}",
        )

    aliases = {
        "skirt__eva_front": {"source_symbol": "skirt", "frame_overrides": {}},
        "skirt__eva_profile": {
            "source_symbol": "skirt",
            "frame_overrides": {
                0: registered_spec("profile", [part_piece(
                    "profile", "skirt", first_element("profile", "skirt", 0)
                )], "approved_design#exact_profile_skirt_alias"),
            },
        },
        "skirt__eva_rear": {"source_symbol": "skirt", "frame_overrides": {}},
        "arm_lower__eva_front": {
            "source_symbol": "arm_lower", "frame_overrides": {},
        },
        "arm_lower__eva_profile": {
            "source_symbol": "arm_lower",
            "frame_overrides": {
                0: registered_spec("profile", [part_piece(
                    "profile", "near_forearm",
                    first_element("profile", "arm_lower", 0, True)
                )], "approved_design#exact_profile_forearm_alias"),
            },
        },
        "arm_lower__eva_rear": {
            "source_symbol": "arm_lower", "frame_overrides": {},
        },
        "hairpigtails__eva_front": {
            "source_symbol": "hairpigtails", "frame_overrides": {},
        },
        "hairpigtails__eva_profile": {
            "source_symbol": "hairpigtails",
            "frame_overrides": {
                2: registered_spec("profile", [part_piece(
                    "profile", "underarm_backing",
                    first_element("profile", "hairpigtails", 2)
                )], "underarm_material#profile_static_hair_and_body_backing"),
            },
        },
        "hairpigtails__eva_rear": {
            "source_symbol": "hairpigtails",
            "frame_overrides": rear_hair_alias_frames,
        },
        # Upper arms and hands are also shared across multiple facings in the
        # native player bank.  Keep complete frame/duration mirrors here so
        # view-specific anatomical registrations can be supplied without
        # changing anim.bin or making one facing's fitted pose leak into
        # another facing.
        "arm_upper__eva_front": {
            "source_symbol": "arm_upper", "frame_overrides": {},
        },
        "arm_upper__eva_profile": {
            "source_symbol": "arm_upper", "frame_overrides": {},
        },
        "arm_upper__eva_rear": {
            "source_symbol": "arm_upper", "frame_overrides": {},
        },
        "hand__eva_front": {
            "source_symbol": "hand", "frame_overrides": {},
        },
        "hand__eva_profile": {
            "source_symbol": "hand", "frame_overrides": {},
        },
        "hand__eva_rear": {
            "source_symbol": "hand", "frame_overrides": {},
        },
    }

    # Controlled front-run trial.  The approved neutral frame stays byte-for-
    # byte in the primary symbols; only the two alternate run chains are
    # registered in the front-facing aliases.  Elbow and wrist are solved
    # against every one of the 16 native run frames, rather than placing art
    # at a donor bbox center or squeezing the hanging sleeve into bone length.
    run_frames = _load_player_clip(builder, PLAYER_BASIC, "run_loop", 8)
    run_groups = _front_run_limb_groups(builder, run_frames)
    upper_elbow = apply(
        inverse(front_upper) @ world["front"],
        regions["front"]["parts"]["left_forearm"]["anchors"]["elbow"],
    )
    limb_trial = _fit_front_run_chain(run_groups, upper_elbow)
    generated_hands = builder.load_sources()["hands"]
    right_lower_element = first_element("front", "arm_lower", 0, True, 1)
    trial_parts = {
        # lower frame, hand frame -> exact concept sleeve, exact concept hand
        # used to derive normalized cuff/fingertip scale, generated pose art.
        (2, 5): ("left_forearm", "left_hand", "fist_palm", front_lower,
                 front_hand),
        (1, 2): ("right_forearm", "right_hand", "grip_side",
                 right_lower_element, right_hand_element),
    }
    for (lower_frame, hand_frame), (
        forearm_name, hand_name, pose_name, neutral_lower_element,
        neutral_hand_element,
    ) in trial_parts.items():
        fitted = limb_trial[(lower_frame, hand_frame)]
        forearm_record = cutouts["front"][f"{forearm_name}_joint"]
        forearm_anchors = regions["front"]["parts"][forearm_name]["anchors"]
        forearm_source = [
            (forearm_anchors[name][0] - forearm_record["origin"][0],
             forearm_anchors[name][1] - forearm_record["origin"][1])
            for name in ("elbow", "wrist")
        ]
        forearm_matrix = _fit_segment_with_fixed_width(
            forearm_source,
            [fitted["lower_elbow"], fitted["lower_wrist"]],
            inverse(neutral_lower_element) @ world["front"],
        )
        aliases["arm_lower__eva_front"]["frame_overrides"][lower_frame] = {
            "pieces": [{
                "image": forearm_record["image"],
                "corners": _corners_from_affine(
                    forearm_record["image"], forearm_matrix
                ),
            }],
            "source": (
                f"approved_design#front_run_forearm_{lower_frame}_"
                "elbow_wrist_least_squares"
            ),
        }

        # Annotate the pose sheet from the approved neutral hand itself: the
        # cuff/wrist and fingertip retain the neutral hand's local separation,
        # while the wrist origin is the native lower-to-hand joint fit.
        hand_record = cutouts["front"][hand_name]
        hand_anchors = regions["front"]["parts"][hand_name]["anchors"]
        exact_wrist = hand_anchors["wrist"]
        exact_tip = hand_anchors["fingertip"]
        neutral_to_local = inverse(neutral_hand_element) @ world["front"]
        neutral_wrist = apply(neutral_to_local, exact_wrist)
        neutral_tip = apply(neutral_to_local, exact_tip)
        fingertip_delta = (
            neutral_tip[0] - neutral_wrist[0],
            neutral_tip[1] - neutral_wrist[1],
        )
        pose_image = generated_hands[pose_name]
        relative_wrist = (
            (exact_wrist[0] - hand_record["origin"][0])
            / hand_record["image"].width,
            (exact_wrist[1] - hand_record["origin"][1])
            / hand_record["image"].height,
        )
        relative_tip = (
            (exact_tip[0] - hand_record["origin"][0])
            / hand_record["image"].width,
            (exact_tip[1] - hand_record["origin"][1])
            / hand_record["image"].height,
        )
        pose_wrist = (relative_wrist[0] * pose_image.width,
                      relative_wrist[1] * pose_image.height)
        pose_tip = (relative_tip[0] * pose_image.width,
                    relative_tip[1] * pose_image.height)
        hand_wrist = fitted["hand_wrist"]
        hand_matrix = fit_similarity(
            [pose_wrist, pose_tip],
            [hand_wrist, (hand_wrist[0] + fingertip_delta[0],
                          hand_wrist[1] + fingertip_delta[1])],
        )
        aliases["hand__eva_front"]["frame_overrides"][hand_frame] = {
            "pieces": [{
                "image": pose_image,
                "corners": _corners_from_affine(pose_image, hand_matrix),
            }],
            "source": (
                f"approved_hands#{pose_name}_front_run_{hand_frame}_"
                "native_wrist_fit"
            ),
        }

    def bind(name, kind, view, symbol, frame, part, anchor, element,
             vertex_offset=0, target_view=None, cutout_part=None,
             target_part=None, source_part=None, source_anchor=None):
        target_view = target_view or view
        target_part = target_part or part
        cutout_part = cutout_part or part
        target = regions[target_view]["parts"][target_part]["anchors"][anchor]
        record = cutouts[view][cutout_part]
        source_part = source_part or part
        source_anchor = source_anchor or anchor
        source_target = regions[view]["parts"][source_part]["anchors"][source_anchor]
        source = (source_target[0] - record["origin"][0],
                  source_target[1] - record["origin"][1])
        binding_rows.append({
            "name": name, "kind": kind, "view": view,
            "symbol": symbol, "frame": frame, "vertex_offset": vertex_offset,
            "normalized": [source[0] / record["image"].width,
                           source[1] / record["image"].height],
            "target": target,
            "element_matrix": element.tolist(),
            "world_matrix": world[view].tolist(),
        })

    bind("front_chin", "chin", "front", "headbase", 0,
         "head_face_crown", "chin", front_head, cutout_part="head_with_crown")
    bind("front_neck", "neckline", "front", "torso", 0, "torso", "neck",
         first_element("front", "torso", 0), cutout_part="torso_with_underarm")
    bind("front_left_shoulder", "shoulder", "front", "arm_upper", 0,
         "left_upper_arm", "shoulder", front_upper)
    bind("front_left_wrist", "wrist", "front", "hand", 0,
         "left_hand", "wrist", front_hand)
    bind("front_waist", "waist", "front", "torso", 0, "torso", "waist",
         first_element("front", "torso", 0), cutout_part="torso_with_underarm")
    bind("front_skirt_waist", "waist", "front", "skirt", 0, "skirt", "waist",
         first_element("front", "skirt", 0))
    bind("front_hem", "hem", "front", "skirt", 0, "skirt", "hem_center",
         first_element("front", "skirt", 0))
    bind("profile_chin", "chin", "profile", "headbase", 1,
         "head_face_crown", "chin", profile_head, cutout_part="head_with_crown")
    bind("profile_neck", "neckline", "profile", "torso", 3, "torso", "neck",
         first_element("profile", "torso", 3), cutout_part="torso_with_underarm")
    bind("profile_shoulder", "shoulder", "profile", "arm_upper", 2,
         "near_upper_arm", "shoulder", first_element("profile", "arm_upper", 2, True))
    bind("profile_elbow", "elbow", "profile", "arm_lower__eva_profile", 0,
         "near_forearm", "elbow", first_element("profile", "arm_lower", 0, True))
    bind("profile_wrist", "wrist", "profile", "hand", 2, "near_hand", "wrist",
         first_element("profile", "hand", 2, True))
    bind("profile_waist", "waist", "profile", "torso", 3, "torso", "waist",
         first_element("profile", "torso", 3), cutout_part="torso_with_underarm")

    # QA-only rows deliberately expose conflicts that cannot be solved by one
    # shared BILD frame. They are reported, never counted as passed anchors.
    bind("front_right_shoulder", "shoulder", "front",
         "arm_upper", 0, "left_upper_arm", "shoulder",
         first_element("front", "arm_upper", 0, True, 1),
         target_part="right_upper_arm", source_part="left_upper_arm")
    bind("front_right_wrist", "wrist", "front",
         "hand", 0, "left_hand", "wrist",
         first_element("front", "hand", 0, True, 1),
         target_part="right_hand", source_part="left_hand")
    bind("profile_hem", "hem", "profile", "skirt__eva_profile", 0,
         "skirt", "hem_center", first_element("profile", "skirt", 0),
         target_view="profile")

    conflicts = specification["shared_frames_to_audit"]
    plan = {
        "version": 1,
        "bindings": binding_rows,
        "shared_frame_conflicts": conflicts,
        "world_map": specification["world_map"],
        "cutout_audit": cutout_audit,
        "source_mode": "approved_design_exact_visible_cutouts",
        "rear_registration": rear_cutouts["audit"],
        "facing_aliases": {name: record["source_symbol"]
                           for name, record in aliases.items()},
        "front_run_limb_trial": {
            f"lower_{lower}_hand_{hand}": record
            for (lower, hand), record in limb_trial.items()
        },
        "front_forearm_partition": front_forearm_partition,
        "unresolved_supported_conflicts": [],
        "accepted_compromises": [
            "front bilateral arm instances share one local frame geometry",
            "rear uses a coherent generated continuity source, not exact approved pixels",
            "rear arms remain the native articulated branch over the coherent gown",
        ],
    }
    Path(plan_path).write_text(json.dumps(plan, indent=2) + "\n", encoding="utf8")
    manifest_path = ARTIFACT / "rig-map.json"
    builder.build_candidate(
        Path(output), registration_overrides=overrides,
        registration_geometry=registration_geometry,
        registration_aliases=aliases,
        manifest_path=manifest_path,
        manifest_extra={
            "registration_plan": str(Path(plan_path).name),
            "expression_geometry": {
                "front_face_frames": [*range(0, 4), *range(8, 14), *range(15, 34)],
                "profile_face_frames": [4, 5, 6, 7],
                "preserved_special_face_frames": [14],
                "cheeks": "unchanged shared puff overlay; front/profile/rear use conflict",
            },
        },
    )
    # Normalize provenance after alias cloning.  Alias fallback frames inherit
    # the truthful source row of their underlying symbol; "candidate" is not
    # a source artifact.  Registered cutouts declare the durable inputs that
    # root copies under assets/source/eva_approved/concept-registration.
    manifest = json.loads(manifest_path.read_text(encoding="utf8"))
    durable = {
        "coherent_rear": REAR_SOURCE,
        "coherent_rear_hat": REAR_HAT_SOURCE,
        "crownless_material": ARTIFACT / "crownless-blank-material.png",
        "blank_skin_material": ARTIFACT / "blank-skin-material.png",
        "underarm_material": ARTIFACT / "underarm-occlusion-plate.png",
        "strand_ownership": STRAND_MASK,
        "rear_strand_ownership": REAR_STRAND_MASK,
    }
    for source_id, path in durable.items():
        manifest["sources"][source_id] = {
            "path": f"concept-registration/{path.name}",
            "sha256": sha256_file(path),
        }
    for alias, alias_record in aliases.items():
        base_rows = {
            row["frame"]: row for row in
            manifest["symbols"][alias_record["source_symbol"]]
        }
        for row in manifest["symbols"][alias]:
            if row["source"].startswith("candidate#"):
                row["source"] = base_rows[row["frame"]]["source"]
    manifest["registration_materials"] = list(durable)
    manifest_path.write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf8"
    )
    return plan


def render_concept_evidence(output_dir=ARTIFACT):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    specification = json.loads(LANDMARKS.read_text(encoding="utf8"))
    parts = _load_builder().load_sources()
    front, front_residuals, front_layers = _render_view("front", parts, specification)
    profile, profile_residuals, profile_layers = _render_view("profile", parts, specification)
    front.save(output_dir / "registered-front-concept-space.png")
    profile.save(output_dir / "registered-profile-concept-space.png")

    reference = Image.open(CONCEPT).convert("RGBA")
    composite = Image.alpha_composite(front, profile)
    overlay = Image.blend(reference, composite, 0.5)
    overlay.save(output_dir / "concept-overlay-50.png")
    side = Image.new("RGBA", (reference.width * 2, reference.height))
    side.alpha_composite(reference, (0, 0))
    side.alpha_composite(composite, (reference.width, 0))
    side.save(output_dir / "concept-side-by-side.png")
    for view, layers in (("front", front_layers), ("profile", profile_layers)):
        for label, layer in layers:
            debug = layer.copy()
            draw = ImageDraw.Draw(debug)
            draw.rectangle((4, 4, 350, 42), fill=(0, 0, 0, 210))
            draw.text((12, 12), f"{view}: {label}", fill=(255, 255, 255, 255))
            debug.save(output_dir / f"debug-{view}-{label}.png")
    return {
        "front": front_residuals,
        "profile": profile_residuals,
        "source_mismatches": [
            "Generated hair strands and gown contours are not pixel-identical to the concept.",
            "Front face nose is an independent residual after fitting eyes and mouth.",
            "Profile repaired head is not consumed until its landmarks are remeasured.",
        ],
    }


def measure_archive(archive, plan_path, landmarks_path):
    """Reconstruct recorded anchors from actual emitted native vertices."""
    plan = json.loads(Path(plan_path).read_text(encoding="utf8"))
    specification = json.loads(Path(landmarks_path).read_text(encoding="utf8"))
    builder = _load_builder()
    from zipfile import ZipFile
    with ZipFile(archive) as bundle:
        build = builder.parse_build(bundle.read("build.bin"))
    results = {}
    for row in plan["bindings"]:
        frame = next(frame for frame in build.symbols[row["symbol"]]
                     if frame.index == row["frame"])
        vertices = frame.vertices[row.get("vertex_offset", 0):]
        if len(vertices) < 6:
            raise ValueError(f"missing quad {row['name']}")
        top_left, top_right, bottom_left = vertices[0], vertices[1], vertices[2]
        nx, ny = row["normalized"]
        local = (
            top_left[0] + nx * (top_right[0] - top_left[0])
            + ny * (bottom_left[0] - top_left[0]),
            top_left[1] + nx * (top_right[1] - top_left[1])
            + ny * (bottom_left[1] - top_left[1]),
        )
        world = apply(np.asarray(row["element_matrix"]), local)
        concept = apply(inverse(np.asarray(row["world_matrix"])), world)
        target = row["target"]
        results[row["name"]] = {
            "kind": row["kind"], "actual": concept, "target": target,
            "error_concept_pixels": distance(concept, target),
        }
    return {
        "archive_sha256": sha256_file(Path(archive)),
        "landmarks": results,
        "shared_frame_conflicts": plan["shared_frame_conflicts"],
        "acceptance": specification["acceptance"],
    }


def render_native_concept_evidence(archive=CANDIDATE, output_dir=ARTIFACT):
    """Render the emitted ZIP through real idle matrices onto the fixed map."""
    renderer_path = TOOLS / "eva/render_player_motion.py"
    if str(renderer_path.parent) not in sys.path:
        sys.path.insert(0, str(renderer_path.parent))
    spec = importlib.util.spec_from_file_location("eva_motion_renderer", renderer_path)
    renderer = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = renderer
    spec.loader.exec_module(renderer)
    build = renderer.load_build_archive(Path(archive))
    alias_contract = renderer.load_contract(
        SOURCE / "facing-aliases.json"
    )
    game_anim = Path(
        "C:/Program Files (x86)/Steam/steamapps/common/Don't Starve Together/data/anim"
    )
    with ZipFile(game_anim / "player_idles.zip") as bundle:
        parsed = renderer.parse_anim(bundle.read("anim.bin"))
    settings = json.loads(LANDMARKS.read_text(encoding="utf8"))
    reference = Image.open(CONCEPT).convert("RGBA")
    rendered = {}
    expression_items = []
    for view, facing in (("front", 8), ("profile", 5)):
        clip = renderer.find_clip(parsed, "idle_loop", facing)
        visibility = renderer.candidate_visibility("normal", overlay=False)
        motion_overrides = renderer.facing_alias_overrides(
            build, alias_contract, facing
        )
        wm = world_matrix(
            settings["world_map"]["scale"],
            settings["world_map"][f"{view}_translation"],
        )
        s, tx, ty = wm[0, 0], wm[0, 2], wm[1, 2]
        native_bounds = (
            math.floor(tx), math.floor(ty),
            math.ceil(tx + s * reference.width),
            math.ceil(ty + s * reference.height),
        )

        def fixed_render(frame):
            native = renderer.render_animation_frame(
                build, frame, visibility, native_bounds, motion_overrides
            )
            coefficients = (s, 0.0, tx - native_bounds[0],
                            0.0, s, ty - native_bounds[1])
            return native.transform(
                reference.size, Image.Transform.AFFINE, coefficients,
                Image.Resampling.BICUBIC,
            )

        image = fixed_render(clip["frames"][8])
        image.save(Path(output_dir) / f"native-{view}-concept-space.png")
        rendered[view] = image
        wanted = set(range(0, 4) if view == "front" else range(4, 8))
        found = {}
        face_hash = renderer.sdbm("face")
        for animation_index, frame in enumerate(clip["frames"]):
            face_indices = [element[1] for element in frame["elements"]
                            if element[0] == face_hash]
            for face_index in face_indices:
                if face_index in wanted and face_index not in found:
                    found[face_index] = animation_index
        left, top, right, bottom = (
            (150, 145, 660, 815) if view == "front"
            else (740, 145, 1212, 815)
        )
        for face_index, animation_index in sorted(found.items()):
            expression_items.append((
                f"{view} face{face_index} / idle{animation_index}",
                fixed_render(clip["frames"][animation_index]).crop(
                    (left, top, right, bottom)
                ),
            ))
    combined = Image.alpha_composite(rendered["front"], rendered["profile"])
    Image.blend(reference, combined, 0.5).save(
        Path(output_dir) / "native-concept-overlay-50.png"
    )
    if expression_items:
        renderer._contact_sheet(
            expression_items,
            "Exact candidate / real idle matrices / fixed concept map",
        ).save(Path(output_dir) / "native-expression-contact.png")
    return {
        "archive_sha256": sha256_file(Path(archive)),
        "world_map": settings["world_map"],
        "expression_samples": [label for label, _ in expression_items],
        "normalization": "none; fixed world-to-concept inverse",
    }


def main():
    ARTIFACT.mkdir(parents=True, exist_ok=True)
    report = render_concept_evidence()
    (ARTIFACT / "source-fit-report.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf8"
    )
    build_registered_candidate()
    measured = measure_archive(CANDIDATE, PLAN, LANDMARKS)
    (ARTIFACT / "archive-landmark-report.json").write_text(
        json.dumps(measured, indent=2) + "\n", encoding="utf8"
    )
    native = render_native_concept_evidence()
    (ARTIFACT / "native-evidence.json").write_text(
        json.dumps(native, indent=2) + "\n", encoding="utf8"
    )
    print(f"Wrote concept evidence to {ARTIFACT}")


if __name__ == "__main__":
    main()
