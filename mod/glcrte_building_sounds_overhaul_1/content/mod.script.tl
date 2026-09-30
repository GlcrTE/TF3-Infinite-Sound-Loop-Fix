-- Building Sounds Overhaul
-- Stops the endlessly repeating drag sound while building streets, tracks and
-- lane modifiers. Instead, every drag (start of dragging / new build point)
-- plays a single 2 second clip made from the original sounds.

local mod = {}

-- vanilla dragStart clip -> replacement clip in this mod's content/sound/
local REPLACEMENTS <const> : {{string, string}} = {
	{ "build/street/drag_start.wav", "street_drag.wav" },
	{ "build/track/drag_start.wav", "track_drag.wav" },
	{ "tool/lane_modifier/drag_start.wav", "lane_modifier_drag.wav" },
}

local clipName = function(clip : any) : string
	if type(clip) == "string" then
		return clip as string
	elseif type(clip) == "table" then
		return (clip as {string : any})["name"] as string
	end
	return nil
end

local findReplacement = function(dragStart : string) : string
	if dragStart == nil then
		return nil
	end
	for __, entry in ipairs(REPLACEMENTS) do
		local suffix = entry[1]
		if dragStart:sub(-#suffix) == suffix then
			return entry[2]
		end
	end
	return nil
end

mod.runFn = function(_captureParams)
	local soundDir = getOwningModId() .. "::/sound/"
	local silence = soundDir .. "silence.wav"

	addModifier("loadBuilderAudioSet", function(_fileName : string, data : {string : any}) : {string : any}
		local replacement = findReplacement(clipName(data["dragStart"]))
		if replacement == nil then
			return data
		end
		data["dragStart"] = soundDir .. replacement
		data["drag"] = { silence }
		if data["dragBridge"] ~= nil then
			data["dragBridge"] = { silence }
		end
		if data["dragTunnel"] ~= nil then
			data["dragTunnel"] = { silence }
		end
		return data
	end)
end

return mod
