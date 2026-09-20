local M = {}

M.RANK = {
    E = 1,
    D = 2,
    C = 3,
    B = 4,
    A = 5,
    S = 6,
}

M.NAMES = {
    [M.RANK.E] = "E",
    [M.RANK.D] = "D",
    [M.RANK.C] = "C",
    [M.RANK.B] = "B",
    [M.RANK.A] = "A",
    [M.RANK.S] = "S",
}

M.LEVEL_REQUIREMENTS = {
    [M.RANK.D] = 10,
    [M.RANK.C] = 20,
    [M.RANK.B] = 30,
    [M.RANK.A] = 40,
    [M.RANK.S] = 50,
}

function M.GetName(rank)
    return M.NAMES[rank] or "E"
end

function M.GetRequiredLevel(rank)
    return M.LEVEL_REQUIREMENTS[rank] or 0
end

function M.GetRankForLevel(level)
    local result = M.RANK.E
    level = tonumber(level) or 1
    for rank = M.RANK.D, M.RANK.S do
        if level >= (M.LEVEL_REQUIREMENTS[rank] or math.huge) then
            result = rank
        end
    end
    return result
end

function M.IsValidRank(rank)
    return type(rank) == "number" and rank >= M.RANK.E and rank <= M.RANK.S
end

function M.GetNextRank(rank)
    if rank < M.RANK.S then
        return rank + 1
    end
    return nil
end

return M
