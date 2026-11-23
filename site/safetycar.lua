-- Race Control: Safety Car (CSP Online Lua Script)
-- All player-facing messages and source comments are in English.
-- This is a testing prototype, not a server-authoritative race-control system.
-- GitHub Actions injects the public Pages base URL during deployment.

local SITE_BASE_URL = '__PAGES_BASE_URL__'
local SOUND_DEPLOYED_URL = SITE_BASE_URL .. '/sc_on.wav'
local SOUND_LIGHTS_OFF_URL = SITE_BASE_URL .. '/sc_lights_off.wav'

local ST_GREEN = 0
local ST_DEPLOYED = 1
local ST_LIGHTS_OFF = 2

local currentStage = ST_GREEN
local bannerRemaining = 0
local BANNER_SECONDS = 5.5

local function makeSoundPlayer(url)
  local ok, playerOrError = pcall(function()
    local player = ui.MediaPlayer()
    player:setSource(url)
    player:setVolume(0.65)
    return player
  end)
  if not ok then
    ac.warn('Race Control: audio player setup failed: ' .. tostring(playerOrError))
    return nil
  end
  return playerOrError
end

local deployedSound = makeSoundPlayer(SOUND_DEPLOYED_URL)
local lightsOffSound = makeSoundPlayer(SOUND_LIGHTS_OFF_URL)

local function playSound(player)
  if not player then return end
  local ok, playbackError = pcall(function()
    player:pause()
    player:setCurrentTime(0)
    player:play()
  end)
  if not ok then
    ac.warn('Race Control: audio playback failed: ' .. tostring(playbackError))
  end
end

local function setStage(stage, playAnnouncement)
  if stage ~= ST_GREEN and stage ~= ST_DEPLOYED and stage ~= ST_LIGHTS_OFF then
    return
  end
  currentStage = stage
  if playAnnouncement then
    bannerRemaining = BANNER_SECONDS
    if stage == ST_DEPLOYED then
      playSound(deployedSound)
    elseif stage == ST_LIGHTS_OFF then
      playSound(lightsOffSound)
    end
  else
    bannerRemaining = 0
  end
end

-- CSP OnlineEvents broadcast messages between connected CSP clients.
-- They are NOT independently authorized by the server. Do not use this
-- prototype to enforce rules or penalties in public competitive events.
local stageEvent = ac.OnlineEvent({
  key = ac.StructItem.key('race_control_safety_car_v2'),
  stage = ac.StructItem.int32(),
}, function(sender, payload)
  -- Avoid playing the same audio twice if the sender receives a local echo.
  local me = ac.getCar(0)
  if sender and me and sender.sessionID == me.sessionID then return end
  setStage(payload.stage, true)
end)

local function broadcastStage(stage)
  -- Apply immediately on the administrator's client.
  setStage(stage, true)
  stageEvent({stage = stage})
end

local function drawAdminControls()
  ui.text('RACE CONTROL | SAFETY CAR')
  ui.text('Send a race-control announcement to connected drivers:')

  if ui.button('SC ON | Safety Car deployed', vec2(320, 34)) then
    broadcastStage(ST_DEPLOYED)
  end
  if ui.button('SC LIGHTS OFF | Prepare to restart', vec2(320, 34)) then
    broadcastStage(ST_LIGHTS_OFF)
  end
  if ui.button('GREEN FLAG | Track clear', vec2(320, 34)) then
    broadcastStage(ST_GREEN)
  end

  local stageName = currentStage == ST_DEPLOYED and 'SAFETY CAR DEPLOYED'
    or currentStage == ST_LIGHTS_OFF and 'SAFETY CAR LIGHTS OFF'
    or 'GREEN FLAG'
  ui.text('Local state: ' .. stageName)
  ui.text('Note: alerts do not control the physical Safety Car or impose penalties.')
end

-- The menu is available in the admin section of CSP's new chat app.
-- This UI flag hides the controls from regular users, but does not provide
-- server-side authentication for online events.
ui.registerOnlineExtra(
  ui.Icons.FastForward,
  'Race Control - Safety Car',
  nil,
  drawAdminControls,
  nil,
  bit.bor(ui.OnlineExtraFlags.Admin, ui.OnlineExtraFlags.Tool)
)

function script.update(dt)
  if bannerRemaining > 0 then
    bannerRemaining = math.max(0, bannerRemaining - dt)
  end
end

local function drawBanner(title, subtitle, isGreen)
  local screen = ac.getUI().windowSize
  local width = math.min(620, math.max(380, screen.x * 0.58))
  local height = 102
  local position = vec2((screen.x - width) * 0.5, math.max(28, screen.y * 0.15))

  ui.beginTransparentWindow('RaceControlSafetyCarBanner', position, vec2(width, height), false)
  local background = isGreen and rgbm(0.10, 0.50, 0.24, 0.97)
    or rgbm(0.96, 0.76, 0.12, 0.97)
  local foreground = isGreen and rgbm.colors.white or rgbm.colors.black
  ui.drawRectFilled(vec2(0, 0), vec2(width, height), background, 8)
  ui.setCursor(vec2(18, 12))
  ui.pushFont(ui.Font.Title)
  ui.textColored(title, foreground)
  ui.popFont()
  ui.setCursor(vec2(18, 62))
  ui.textColored(subtitle, foreground)
  ui.endTransparentWindow()
end

local function drawStatusBadge()
  local screen = ac.getUI().windowSize
  local size = vec2(242, 42)
  local position = vec2((screen.x - size.x) * 0.5, 18)
  ui.beginTransparentWindow('RaceControlSafetyCarIndicator', position, size, false)
  ui.drawRectFilled(vec2(0, 0), size, rgbm(0.96, 0.76, 0.12, 0.94), 6)
  ui.setCursor(vec2(14, 11))
  local label = currentStage == ST_DEPLOYED and 'SC ACTIVE'
    or 'SC ACTIVE | LIGHTS OFF'
  ui.textColored(label, rgbm.colors.black)
  ui.endTransparentWindow()
end

function script.drawUI()
  if bannerRemaining > 0 then
    if currentStage == ST_DEPLOYED then
      drawBanner('SAFETY CAR DEPLOYED', 'SLOW DOWN - NO OVERTAKING', false)
    elseif currentStage == ST_LIGHTS_OFF then
      drawBanner('SAFETY CAR LIGHTS OFF', 'PREPARE TO RESTART - NO OVERTAKING', false)
    else
      drawBanner('GREEN FLAG - TRACK CLEAR', 'RACING RESUMED', true)
    end
  elseif currentStage ~= ST_GREEN then
    drawStatusBadge()
  end
end
