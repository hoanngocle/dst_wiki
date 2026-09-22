"""Regression tests for concept-coordinate EVA registration.

The integration assertion reconstructs landmarks from the emitted BILD and
the real idle frame matrices.  It intentionally does not trust residuals
written by the builder itself.
"""

import json
import math
import os
from pathlib import Path
import sys
import unittest
from hashlib import sha256
from zipfile import ZipFile

import numpy as np
from PIL import Image


TOOLS = Path(__file__).resolve().parent
MOD = TOOLS.parent
SOURCE = MOD / "assets/source/eva_approved"
ARTIFACT = SOURCE / "concept-registration"
sys.path.insert(0, str(TOOLS))

import register_eva_concept as registration


LANDMARKS = ARTIFACT / "landmarks.json"
PLAN = ARTIFACT / "registration-plan.json"
CANDIDATE = Path(os.environ.get(
    "EVA_REGISTRATION_ARCHIVE",
    MOD / "anim/eva.zip",
))
BASELINE_EVA = SOURCE / "baseline-eva.zip"
BASELINE_SHA256 = "8e9dea6643f469fb61f07be6b67b671162ed04a149d27abae012fb0957fa323f"


class EvaConceptRegistrationTest(unittest.TestCase):
    def test_homogeneous_native_roundtrip_uses_one_world_map(self):
        concept = (417.0, 501.0)
        world_map = registration.world_matrix(0.8, (-333.6, -538.8))
        element = registration.element_matrix((0.91, 0.40, -0.40, 0.91,
                                               -20.01, -109.11))
        native = registration.apply(
            registration.inverse(element),
            registration.apply(world_map, concept),
        )
        reconstructed = registration.apply(
            registration.inverse(world_map),
            registration.apply(element, native),
        )
        self.assertAlmostEqual(reconstructed[0], concept[0], places=5)
        self.assertAlmostEqual(reconstructed[1], concept[1], places=5)

    def test_segment_fit_preserves_neutral_handedness_at_all_rotations(self):
        source = [(0.0, 0.0), (0.0, 10.0)]
        cases = (
            (((1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0)),
             [(2.0, 3.0), (2.0, 23.0)], 1),
            (((1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0)),
             [(2.0, 3.0), (-18.0, 3.0)], 1),
            (((1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0)),
             [(2.0, 3.0), (2.0, -17.0)], 1),
            (((-1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0)),
             [(2.0, 3.0), (2.0, 23.0)], -1),
        )
        for neutral, target, expected_sign in cases:
            fitted = registration._fit_segment_with_fixed_width(
                source, target, neutral
            )
            self.assertAlmostEqual(
                math.copysign(1.0, float(__import__("numpy").linalg.det(
                    fitted[:2, :2]
                ))),
                expected_sign,
            )
            for source_point, target_point in zip(source, target):
                actual = registration.apply(fitted, source_point)
                self.assertAlmostEqual(actual[0], target_point[0], places=6)
                self.assertAlmostEqual(actual[1], target_point[1], places=6)

    def test_source_landmark_fits_are_explicit_and_report_residuals(self):
        data = json.loads(LANDMARKS.read_text(encoding="utf8"))
        face = data["source_parts"]["front"]["face"]
        fitted = registration.fit_affine(
            [face["anchors"][name] for name in ("left_eye", "right_eye", "mouth")],
            [face["targets"][name] for name in ("left_eye", "right_eye", "mouth")],
        )
        residual = registration.distance(
            registration.apply(fitted, face["anchors"]["nose"]),
            face["targets"]["nose"],
        )
        self.assertGreater(residual, 6.0, "nose contour mismatch must stay visible")

    def test_cutout_masks_preserve_original_pixels_and_concept_origin(self):
        source = Image.new("RGBA", (8, 6))
        source.putdata([
            (x * 17, y * 23, 91, 255 if 1 <= x <= 6 and 1 <= y <= 4 else 0)
            for y in range(6) for x in range(8)
        ])
        regions = {
            "precedence": ["hair", "face"],
            "parts": {
                "hair": {"polygon": [[0, 0], [5, 0], [5, 5], [0, 5]]},
                "face": {"polygon": [[3, 0], [7, 0], [7, 5], [3, 5]]},
            },
        }
        cutouts, audit = registration.extract_cutouts(source, regions)
        self.assertEqual(cutouts["hair"]["origin"], (1, 1))
        self.assertEqual(cutouts["face"]["origin"], (6, 1))
        for record in cutouts.values():
            image = record["image"]
            ox, oy = record["origin"]
            for y in range(image.height):
                for x in range(image.width):
                    pixel = image.getpixel((x, y))
                    if pixel[3]:
                        self.assertEqual(pixel, source.getpixel((ox + x, oy + y)))
        self.assertEqual(audit["overlap_pixels_before_precedence"], 12)
        self.assertEqual(audit["changed_rgb_pixels"], 0)

    def test_exact_cutouts_preserve_visible_rgb_and_leave_small_audited_gaps(self):
        _, audits = registration.build_exact_cutouts()
        for view in ("front", "profile"):
            self.assertEqual(audits[view]["changed_rgb_pixels"], 0)
            self.assertLess(audits[view]["unassigned_visible_pixels"], 400)

    def test_coherent_rear_split_preserves_source_pixels_and_overlap_contract(self):
        records = registration.build_coherent_rear_cutouts()
        source = Image.open(registration.REAR_SOURCE).convert("RGBA")
        hat_source = Image.open(registration.REAR_HAT_SOURCE).convert("RGBA")
        for name in ("head", "left_hair", "right_hair", "torso", "skirt"):
            record = records[name]
            ox, oy = record["origin"]
            image = record["image"]
            for y in range(image.height):
                for x in range(image.width):
                    pixel = image.getpixel((x, y))
                    if pixel[3]:
                        self.assertEqual(pixel, source.getpixel((ox + x, oy + y)))
        record = records["head_hat"]
        ox, oy = record["origin"]
        for y in range(record["image"].height):
            for x in range(record["image"].width):
                pixel = record["image"].getpixel((x, y))
                if pixel[3]:
                    self.assertEqual(pixel, hat_source.getpixel((ox + x, oy + y)))
        audit = records["audit"]
        self.assertEqual(audit["unassigned_alpha32_pixels"], 0)
        self.assertEqual(audit["strand_unassigned_pixels"], 0)
        self.assertIn("frames 0 and 1", audit["motion_owner"])
        self.assertTrue(audit["source_rgb_preserved"])

    def test_front_forearm_partition_is_exact_and_non_overlapping(self):
        cutouts, _ = registration.build_exact_cutouts()
        regions = json.loads(
            (ARTIFACT / "concept-cutout-regions.json").read_text(encoding="utf8")
        )
        for name in ("left_forearm", "right_forearm"):
            original = cutouts["front"][name]
            joint, pendant, audit = registration._split_forearm_joint_and_pendant(
                original, regions["front"]["parts"][name]["anchors"]
            )
            original_pixels = np.asarray(original["image"], dtype=np.uint8)
            joint_pixels = np.asarray(joint["image"], dtype=np.uint8)
            pendant_pixels = np.asarray(pendant["image"], dtype=np.uint8)
            original_alpha = original_pixels[:, :, 3] > 0
            joint_alpha = joint_pixels[:, :, 3] > 0
            pendant_alpha = pendant_pixels[:, :, 3] > 0
            self.assertFalse(np.any(joint_alpha & pendant_alpha))
            self.assertTrue(np.array_equal(
                joint_alpha | pendant_alpha, original_alpha
            ))
            reconstructed = np.where(
                joint_alpha[:, :, None], joint_pixels, pendant_pixels
            )
            self.assertTrue(np.array_equal(reconstructed, original_pixels))
            self.assertTrue(audit["union_exact"])
            self.assertEqual(audit["overlap_pixels"], 0)

    def test_candidate_landmarks_are_reconstructed_from_emitted_zip(self):
        self.assertTrue(CANDIDATE.is_file(), CANDIDATE)
        self.assertTrue(PLAN.is_file(), PLAN)
        report = registration.measure_archive(CANDIDATE, PLAN, LANDMARKS)
        critical = {
            name: row for name, row in report["landmarks"].items()
            if row["kind"] in {
                "chin", "neckline", "shoulder", "elbow", "wrist", "waist", "hem"
            }
        }
        self.assertGreaterEqual(len(critical), 12)
        self.assertLessEqual(
            max(row["error_concept_pixels"] for row in critical.values()),
            6.0,
            critical,
        )
        self.assertEqual(report["archive_sha256"], registration.sha256_file(CANDIDATE))
        self.assertTrue(report["shared_frame_conflicts"])
        plan = json.loads(PLAN.read_text(encoding="utf8"))
        self.assertEqual(plan["unresolved_supported_conflicts"], [])
        self.assertIn("profile_hem", critical)
        self.assertIn("front_right_wrist", critical)
        plan = json.loads(PLAN.read_text(encoding="utf8"))
        limb_trial = plan["front_run_limb_trial"]
        self.assertEqual(set(limb_trial), {
            "lower_1_hand_2", "lower_2_hand_5",
        })
        self.assertLessEqual(max(
            row["max_elbow_error_native"] for row in limb_trial.values()
        ), 20.0)
        self.assertLessEqual(max(
            row["max_wrist_error_native"] for row in limb_trial.values()
        ), 5.1)

    def test_facing_aliases_keep_complete_frame_duration_coverage(self):
        builder = registration._load_builder()
        from zipfile import ZipFile
        with ZipFile(CANDIDATE) as bundle:
            build = builder.parse_build(bundle.read("build.bin"))
        plan = json.loads(PLAN.read_text(encoding="utf8"))
        expected_aliases = {
            f"{symbol}__eva_{view}"
            for symbol in (
                "skirt", "arm_lower", "hairpigtails", "arm_upper", "hand"
            )
            for view in ("front", "profile", "rear")
        }
        self.assertEqual(set(plan["facing_aliases"]), expected_aliases)
        self.assertTrue(expected_aliases.issubset(build.symbols))
        for alias, source in plan["facing_aliases"].items():
            expected = [(frame.index, frame.duration)
                        for frame in build.symbols[source]]
            actual = [(frame.index, frame.duration)
                      for frame in build.symbols[alias]]
            self.assertEqual(actual, expected, alias)
        rear_hair = {frame.index: frame
                     for frame in build.symbols["hairpigtails__eva_rear"]}
        self.assertGreater(len(rear_hair[0].vertices), 0)
        self.assertGreater(len(rear_hair[1].vertices), 0)

    def test_candidate_keeps_eva_identity_two_atlases_and_animation_bytes(self):
        self.assertEqual(registration.sha256_file(BASELINE_EVA), BASELINE_SHA256)
        builder = registration._load_builder()
        with ZipFile(CANDIDATE) as candidate, ZipFile(BASELINE_EVA) as baseline:
            build = builder.parse_build(candidate.read("build.bin"))
            self.assertEqual(build.name, "eva")
            self.assertEqual(build.atlases, ["atlas-0.tex", "atlas-1.tex"])
            self.assertEqual(
                sha256(candidate.read("anim.bin")).hexdigest(),
                sha256(baseline.read("anim.bin")).hexdigest(),
            )


if __name__ == "__main__":
    unittest.main()
