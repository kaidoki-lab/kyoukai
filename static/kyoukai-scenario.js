(function () {
  "use strict";

  var STORAGE_KEY = "kyoukai_scenario_state_v1";
  var building = window.KYOUKAI_BUILDING || { roomsPerFloor: 5, rooms: [], initialScenarioFloors: 3 };
  var events = window.KYOUKAI_SCENARIO_EVENTS || { phoneEvents: [], managerEvents: [], roomEvents: [], routes: [], diaryEntries: [] };
  var roomsPerFloor = Number(building.roomsPerFloor || 5);
  var passiveRooms = { home: true, elevator: true, floor: true };
  var currentRoomId = window.KYOUKAI_ROOM || null;

  function clone(value) {
    return JSON.parse(JSON.stringify(value));
  }

  function normalizeNumber(value, fallback) {
    var number = Number(value);
    return Number.isFinite(number) ? number : fallback;
  }

  function calculatePlacement(roomIndex) {
    var index = normalizeNumber(roomIndex, 0);
    return {
      floor: Math.floor(index / roomsPerFloor) + 1,
      slot: index % roomsPerFloor + 1
    };
  }

  function getFloorId(floorNumber) {
    return "floor_" + String(Number(floorNumber || 0)).padStart(2, "0");
  }

  function floorIdToNumber(floorId) {
    var match = String(floorId || "").match(/(\d+)/);
    return match ? Number(match[1]) : null;
  }

  function getRooms() {
    return (building.rooms || []).map(function (room) {
      var next = Object.assign({}, room);
      var placement = calculatePlacement(next.roomIndex);
      next.floor = placement.floor;
      next.slot = placement.slot;
      return next;
    }).sort(function (a, b) {
      return a.roomIndex - b.roomIndex;
    });
  }

  function nextRoomIndex(rooms) {
    var list = Array.isArray(rooms) ? rooms : getRooms();
    if (!list.length) return 0;
    return list.reduce(function (max, room) {
      return Math.max(max, normalizeNumber(room.roomIndex, -1));
    }, -1) + 1;
  }

  function createRoomRecord(room, index) {
    var nextIndex = typeof room.roomIndex === "number" ? room.roomIndex : index;
    var next = Object.assign({}, room, { roomIndex: nextIndex });
    var placement = calculatePlacement(next.roomIndex);
    next.floor = placement.floor;
    next.slot = placement.slot;
    return next;
  }

  function getMaxFloor() {
    var maxRoomFloor = getRooms().reduce(function (max, room) {
      return Math.max(max, room.floor);
    }, 1);
    return Math.max(maxRoomFloor, Number(building.initialScenarioFloors || 3));
  }

  function groupRoomsByFloor() {
    var floors = {};
    getRooms().forEach(function (room) {
      var floorKey = String(room.floor).padStart(2, "0");
      if (!floors[floorKey]) floors[floorKey] = [];
      floors[floorKey][room.slot - 1] = room;
    });
    return floors;
  }

  function defaultFloorStates() {
    var states = {};
    var maxFloor = getMaxFloor();
    var unlockedUntil = Number((building.floorStates && building.floorStates.unlockedUntil) || building.initialScenarioFloors || 3);
    for (var floor = 1; floor <= maxFloor; floor += 1) {
      states[String(floor).padStart(2, "0")] = floor <= unlockedUntil ? "unlocked" : "story_only";
    }
    return states;
  }

  function defaultUnlockedFloorIds() {
    var list = [];
    var unlockedUntil = Number((building.floorStates && building.floorStates.unlockedUntil) || building.initialScenarioFloors || 3);
    for (var floor = 1; floor <= unlockedUntil; floor += 1) {
      list.push(getFloorId(floor));
    }
    return list;
  }

  function defaultRoomStates() {
    return getRooms().reduce(function (states, room) {
      states[room.id] = room.defaultState || "normal";
      return states;
    }, {});
  }

  function defaultResidentStates() {
    return (building.residents || []).reduce(function (states, resident) {
      states[resident.id] = resident.state || "hidden";
      return states;
    }, {});
  }

  function defaultRouteStatus() {
    return (events.routes || []).reduce(function (statuses, route) {
      statuses[route.route_id || route.id] = route.status_default || "not_started";
      return statuses;
    }, { route_a: "not_started" });
  }

  function createDefaultState() {
    var roomStates = defaultRoomStates();
    return {
      schema_version: 1,
      mode: null,
      first_room_id: null,
      active_route_id: null,
      route_status: defaultRouteStatus(),
      event_status: {},
      enabled_event_ids: [],
      room_states: roomStates,
      unlocked_floor_ids: defaultUnlockedFloorIds(),
      completed_scenario_count: 0,
      current_target_room_id: null,
      active_phone_event_id: null,
      phone_state: "idle",
      manager_state: "hidden",
      last_completed_event_id: null,
      diary_entry_ids: [],
      phone_ignore_count: 0,
      phone_pool_enabled: [],
      room_entry_history: [],
      interaction_history: [],
      sequence_history: [],
      current_route: null,
      current_chapter: null,
      current_event: null,
      room_state: roomStates,
      floor_state: defaultFloorStates(),
      resident_state: defaultResidentStates(),
      items: [],
      unlocked_rooms: [],
      conversation_history: [],
      completed_events: [],
      progress_rate: 0,
      updated_at: new Date().toISOString()
    };
  }

  function unique(list) {
    return Array.from(new Set(Array.isArray(list) ? list.filter(Boolean) : []));
  }

  function normalizeState(state) {
    var defaults = createDefaultState();
    var next = Object.assign(defaults, state || {});
    next.schema_version = 1;
    next.route_status = Object.assign(defaultRouteStatus(), next.route_status || {});
    next.event_status = Object.assign({}, next.event_status || {});
    next.enabled_event_ids = unique(next.enabled_event_ids);
    next.unlocked_floor_ids = unique(next.unlocked_floor_ids);
    next.diary_entry_ids = unique(next.diary_entry_ids);
    next.phone_pool_enabled = unique(next.phone_pool_enabled);
    next.unlocked_rooms = unique(next.unlocked_rooms);
    next.completed_events = unique(next.completed_events);
    next.conversation_history = Array.isArray(next.conversation_history) ? next.conversation_history : [];
    next.room_entry_history = Array.isArray(next.room_entry_history) ? next.room_entry_history : [];
    next.interaction_history = Array.isArray(next.interaction_history) ? next.interaction_history : [];
    next.sequence_history = Array.isArray(next.sequence_history) ? next.sequence_history : [];
    next.room_states = Object.assign(defaultRoomStates(), next.room_states || next.room_state || {});
    next.room_state = next.room_states;
    next.floor_state = Object.assign(defaultFloorStates(), next.floor_state || {});

    next.completed_events.forEach(function (eventId) {
      next.event_status[eventId] = "completed";
    });
    Object.keys(next.event_status).forEach(function (eventId) {
      if (next.event_status[eventId] === "completed" && next.completed_events.indexOf(eventId) === -1) {
        next.completed_events.push(eventId);
      }
      if (next.event_status[eventId] === "enabled" && next.enabled_event_ids.indexOf(eventId) === -1) {
        next.enabled_event_ids.push(eventId);
      }
    });
    Object.keys(next.floor_state).forEach(function (floorKey) {
      if (["unlocked", "completed"].indexOf(next.floor_state[floorKey]) !== -1) {
        var floorId = getFloorId(floorKey);
        if (next.unlocked_floor_ids.indexOf(floorId) === -1) next.unlocked_floor_ids.push(floorId);
      }
    });
    next.unlocked_floor_ids.forEach(function (floorId) {
      var floorNumber = floorIdToNumber(floorId);
      if (floorNumber) next.floor_state[String(floorNumber).padStart(2, "0")] = "unlocked";
    });
    next.current_route = next.active_route_id;
    next.progress_rate = Math.round((next.completed_events.length / Math.max(1, allEvents().length)) * 100);
    return next;
  }

  function getState() {
    try {
      var saved = window.localStorage.getItem(STORAGE_KEY);
      if (!saved) return createDefaultState();
      return normalizeState(JSON.parse(saved));
    } catch (error) {
      console.warn("[KYOUKAI] scenario state reset:", error);
      return createDefaultState();
    }
  }

  function saveState(state) {
    var next = normalizeState(state || {});
    next.updated_at = new Date().toISOString();
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(next));
    document.dispatchEvent(new CustomEvent("kyoukai:scenario-state", { detail: clone(next) }));
    return next;
  }

  function startMode(mode, firstRoomId) {
    var state = getState();
    if (state.mode) return state;
    state.mode = mode;
    state.first_room_id = firstRoomId || currentRoomId || null;
    if (mode === "scenario") {
      state.active_route_id = null;
      state.current_route = null;
      state.current_chapter = null;
      state.route_status.route_a = state.route_status.route_a || "not_started";
      state.manager_state = "hidden";
      state.phone_state = "idle";
      state.floor_state = defaultFloorStates();
      state.unlocked_floor_ids = defaultUnlockedFloorIds();
      if (state.enabled_event_ids.indexOf("route_a_phone_001") === -1) state.enabled_event_ids.push("route_a_phone_001");
      state.event_status.route_a_phone_001 = state.event_status.route_a_phone_001 || "enabled";
    }
    if (mode === "free") {
      getRooms().forEach(function (room) {
        if (state.unlocked_rooms.indexOf(room.id) === -1) state.unlocked_rooms.push(room.id);
        state.room_states[room.id] = state.room_states[room.id] === "disabled" ? "disabled" : "normal";
        state.floor_state[String(room.floor).padStart(2, "0")] = "unlocked";
        var floorId = getFloorId(room.floor);
        if (state.unlocked_floor_ids.indexOf(floorId) === -1) state.unlocked_floor_ids.push(floorId);
      });
    }
    return saveState(state);
  }

  function maybeSetInitialMode(roomId) {
    var state = getState();
    if (state.mode || !roomId || passiveRooms[roomId]) return state;
    return startMode(roomId === "kanrinin" ? "scenario" : "free", roomId);
  }

  function roomById(roomId) {
    return getRooms().find(function (room) {
      return room.id === roomId;
    }) || null;
  }

  function roomByHref(href) {
    if (!href) return null;
    var path = href;
    try {
      path = new URL(href, window.location.origin).pathname;
    } catch (error) {}
    return getRooms().find(function (room) {
      var roomPath = new URL(room.href, window.location.origin).pathname;
      return roomPath === path;
    }) || null;
  }

  function canEnterFloor(floorNumber) {
    var state = getState();
    if (state.mode !== "scenario") return true;
    var number = Number(floorNumber);
    var key = String(number).padStart(2, "0");
    return ["unlocked", "completed"].indexOf(state.floor_state[key]) !== -1 || state.unlocked_floor_ids.indexOf(getFloorId(number)) !== -1;
  }

  function canEnterRoom(roomId) {
    var state = getState();
    if (state.mode !== "scenario") return true;
    var room = roomById(roomId);
    if (!room) return true;
    if (!canEnterFloor(room.floor)) return false;
    var roomState = state.room_states[roomId] || room.defaultState || "normal";
    if (roomState === "disabled") return false;
    return ["normal", "waiting", "active", "completed", "post_route_a", "signal_contaminated", "observation_signal_received"].indexOf(roomState) !== -1 || state.unlocked_rooms.indexOf(roomId) !== -1;
  }

  function showNotice(message) {
    var event = new CustomEvent("kyoukai:scenario-notice", { detail: { message: message } });
    document.dispatchEvent(event);
    if (!event.defaultPrevented) {
      window.alert(message);
    }
  }

  function allEvents() {
    return [].concat(events.phoneEvents || [], events.roomEvents || [], events.managerEvents || []);
  }

  function getEventById(eventId) {
    return allEvents().find(function (event) {
      return event.event_id === eventId;
    }) || null;
  }

  function requirementWarn(requirement) {
    console.warn("[KYOUKAI] unsupported scenario requirement:", requirement);
    return false;
  }

  function compareSeconds(actual, operator, expected) {
    if (operator === ">=") return actual >= expected;
    if (operator === ">") return actual > expected;
    if (operator === "<=") return actual <= expected;
    if (operator === "<") return actual < expected;
    return actual === expected;
  }

  function requirementsMet(requirements, state, context) {
    var ctx = context || {};
    return (requirements || []).every(function (requirement) {
      if (requirement.type === "mode") return state.mode === requirement.value;
      if (requirement.type === "mode_equals") return state.mode === requirement.value;
      if (requirement.type === "first_room_equals") return state.first_room_id === requirement.room_id;
      if (requirement.type === "route_status_equals") return state.route_status[requirement.route_id] === requirement.value;
      if (requirement.type === "active_route_equals") return state.active_route_id === requirement.value;
      if (requirement.type === "active_phone_event_equals") return state.active_phone_event_id === requirement.value;
      if (requirement.type === "event_completed") return state.event_status[requirement.event_id] === "completed" || state.completed_events.indexOf(requirement.event_id) !== -1;
      if (requirement.type === "event_not_completed") return state.event_status[requirement.event_id] !== "completed" && state.completed_events.indexOf(requirement.event_id) === -1;
      if (requirement.type === "event_enabled") return state.enabled_event_ids.indexOf(requirement.event_id) !== -1 || state.event_status[requirement.event_id] === "enabled";
      if (requirement.type === "room_state") return state.room_states[requirement.room || requirement.room_id] === requirement.state;
      if (requirement.type === "floor_state") return state.floor_state[String(requirement.floor).padStart(2, "0")] === requirement.state;
      if (requirement.type === "room_stay_seconds") return compareSeconds(Number(ctx.roomStaySeconds || 0), requirement.operator || ">=", Number(requirement.value || 0));
      if (requirement.type === "room_entered") return state.room_entry_history.some(function (entry) { return entry.room_id === requirement.room_id; });
      if (requirement.type === "interaction_completed") return state.interaction_history.indexOf(requirement.target) !== -1 || ctx.interactionTarget === requirement.target;
      if (requirement.type === "sequence_finished") return state.sequence_history.indexOf(requirement.event_id) !== -1 || ctx.sequenceEventId === requirement.event_id;
      if (requirement.type === "room_entered_after_event") {
        return currentRoomId === requirement.room_id && state.last_completed_event_id === requirement.after_event_id;
      }
      return requirementWarn(requirement);
    });
  }

  function getNextPhoneEvent(context) {
    var state = getState();
    if (state.mode !== "scenario") return null;
    return (events.phoneEvents || []).filter(function (event) {
      return state.enabled_event_ids.indexOf(event.event_id) !== -1 && requirementsMet(event.requirements, state, context || {});
    }).sort(function (a, b) {
      return Number(b.priority || 0) - Number(a.priority || 0);
    })[0] || null;
  }

  function setEventStatus(state, eventId, status) {
    if (!eventId) return;
    state.event_status[eventId] = status;
    if (status === "enabled" && state.enabled_event_ids.indexOf(eventId) === -1) state.enabled_event_ids.push(eventId);
    if (status === "completed" && state.completed_events.indexOf(eventId) === -1) state.completed_events.push(eventId);
  }

  function unlockFloor(state, floorId) {
    var floorNumber = floorIdToNumber(floorId);
    if (!floorNumber) return;
    var normalized = getFloorId(floorNumber);
    if (state.unlocked_floor_ids.indexOf(normalized) === -1) state.unlocked_floor_ids.push(normalized);
    state.floor_state[String(floorNumber).padStart(2, "0")] = "unlocked";
    getRooms().forEach(function (room) {
      if (room.floor !== floorNumber) return;
      if (state.room_states[room.id] !== "disabled") state.room_states[room.id] = "normal";
      if (state.unlocked_rooms.indexOf(room.id) === -1) state.unlocked_rooms.push(room.id);
    });
  }

  function applyEffect(state, effect) {
    if (!effect || !effect.type) return true;
    if (effect.type === "set_phone_state") state.phone_state = effect.value;
    else if (effect.type === "set_current_event") state.current_event = effect.event_id;
    else if (effect.type === "set_manager_state") state.manager_state = effect.state || effect.value;
    else if (effect.type === "set_room_state") state.room_states[effect.room_id || effect.room] = effect.value || effect.state;
    else if (effect.type === "set_route_status") state.route_status[effect.route_id] = effect.value;
    else if (effect.type === "set_active_route") state.active_route_id = effect.route_id || null;
    else if (effect.type === "complete_event") {
      setEventStatus(state, effect.event_id, "completed");
      state.last_completed_event_id = effect.event_id;
    } else if (effect.type === "enable_event") setEventStatus(state, effect.event_id, "enabled");
    else if (effect.type === "set_target_room") state.current_target_room_id = effect.room_id;
    else if (effect.type === "clear_target_room") state.current_target_room_id = null;
    else if (effect.type === "append_diary_entry") {
      if (state.diary_entry_ids.indexOf(effect.entry_id) === -1) state.diary_entry_ids.push(effect.entry_id);
    } else if (effect.type === "unlock_floor") unlockFloor(state, effect.floor_id);
    else if (effect.type === "increment_counter") state[effect.counter_id] = Number(state[effect.counter_id] || 0) + Number(effect.value || 1);
    else if (effect.type === "enable_phone_pool") {
      if (state.phone_pool_enabled.indexOf(effect.pool_id) === -1) state.phone_pool_enabled.push(effect.pool_id);
    } else if (effect.type === "unlock_room") {
      var room = roomById(effect.room);
      if (state.unlocked_rooms.indexOf(effect.room) === -1) state.unlocked_rooms.push(effect.room);
      if (room) unlockFloor(state, getFloorId(room.floor));
    } else {
      console.warn("[KYOUKAI] unsupported scenario effect:", effect);
      return false;
    }
    return true;
  }

  function applyEffects(eventData, context) {
    if (!eventData) return getState();
    var state = getState();
    var ok = requirementsMet(eventData.completion_requirements || [], state, context || {});
    if (!ok && eventData.completion_requirements && eventData.completion_requirements.length) {
      console.warn("[KYOUKAI] completion requirements not met:", eventData.event_id);
      return state;
    }
    (eventData.effects || []).every(function (effect) {
      return applyEffect(state, effect);
    });
    state.current_event = state.current_event === eventData.event_id ? null : state.current_event;
    state.phone_state = state.phone_state === "ended" ? "idle" : state.phone_state;
    return saveState(state);
  }

  function startPhoneRinging(eventId) {
    var state = getState();
    if (state.phone_state !== "idle" || state.active_phone_event_id) return state;
    state.phone_state = "ringing";
    state.active_phone_event_id = eventId;
    return saveState(state);
  }

  function cancelPhoneRinging() {
    var state = getState();
    if (state.phone_state === "ringing" && state.active_phone_event_id) {
      state.phone_ignore_count = Number(state.phone_ignore_count || 0) + 1;
      state.phone_state = "idle";
      state.active_phone_event_id = null;
      return saveState(state);
    }
    return state;
  }

  function acceptPhoneEvent(eventId) {
    var event = getEventById(eventId);
    if (!event) return null;
    var state = getState();
    if (state.phone_state !== "ringing" || state.active_phone_event_id !== eventId) return null;
    state.phone_state = "conversation";
    state.current_event = eventId;
    state.conversation_history.push({
      event_id: event.event_id,
      caller: event.caller_display_name || event.caller,
      lines: event.conversation || [],
      at: new Date().toISOString()
    });
    saveState(state);
    return event;
  }

  function finishPhoneEvent(eventId) {
    var event = getEventById(eventId);
    if (!event) return getState();
    var state = getState();
    state.phone_state = "ended";
    state.active_phone_event_id = null;
    state.current_event = eventId;
    saveState(state);
    state = applyEffects(event, { sequenceEventId: eventId });
    state.phone_state = "idle";
    state.active_phone_event_id = null;
    return saveState(state);
  }

  function completeScenarioEvent(eventId, context) {
    var event = getEventById(eventId);
    if (!event) return getState();
    var state = getState();
    if (context && context.interactionTarget && state.interaction_history.indexOf(context.interactionTarget) === -1) {
      state.interaction_history.push(context.interactionTarget);
    }
    if (context && context.sequenceEventId && state.sequence_history.indexOf(context.sequenceEventId) === -1) {
      state.sequence_history.push(context.sequenceEventId);
    }
    saveState(state);
    return applyEffects(event, context || {});
  }

  function markRoomEntered(roomId) {
    if (!roomId || passiveRooms[roomId]) return getState();
    var state = getState();
    state.room_entry_history.push({ room_id: roomId, at: new Date().toISOString() });
    return saveState(state);
  }

  function getActiveRoomEvent(roomId) {
    var state = getState();
    if (state.mode !== "scenario") return null;
    return (events.roomEvents || []).find(function (event) {
      return event.room_id === roomId && requirementsMet(event.requirements, state, {});
    }) || null;
  }

  function getManagerEvent(roomId) {
    var state = getState();
    if (state.mode !== "scenario") return null;
    return (events.managerEvents || []).find(function (event) {
      return event.room_id === roomId && requirementsMet(event.requirements, state, {});
    }) || null;
  }

  function setRoomEventActive(eventId) {
    var event = getEventById(eventId);
    if (!event || !event.room_id) return getState();
    var state = getState();
    state.room_states[event.room_id] = event.room_state_during || "active";
    state.current_event = eventId;
    return saveState(state);
  }

  function getDiaryEntries() {
    var state = getState();
    var diaryMap = (events.diaryEntries || []).reduce(function (map, entry) {
      map[entry.entry_id] = entry;
      return map;
    }, {});
    return state.diary_entry_ids.map(function (entryId) {
      return diaryMap[entryId];
    }).filter(Boolean).map(function (entry) {
      return {
        entry_id: entry.entry_id,
        category: "Route_A",
        title: entry.title || "混線している観測",
        body: entry.text
      };
    });
  }

  function bindNavigationGuard() {
    document.addEventListener("click", function (event) {
      var anchor = event.target.closest("a[href]");
      if (!anchor) return;
      var room = roomByHref(anchor.getAttribute("href"));
      if (!room) return;
      maybeSetInitialMode(room.id);
      if (canEnterRoom(room.id)) return;
      event.preventDefault();
      event.stopImmediatePropagation();
      showNotice("この階はまだ閉鎖されています。管理人室の着信を待ってください。");
    }, true);
  }

  function init() {
    maybeSetInitialMode(currentRoomId);
    markRoomEntered(currentRoomId);
    bindNavigationGuard();
  }

  window.KYOUKAI_SCENARIO = {
    STORAGE_KEY: STORAGE_KEY,
    calculatePlacement: calculatePlacement,
    nextRoomIndex: nextRoomIndex,
    createRoomRecord: createRoomRecord,
    getRooms: getRooms,
    groupRoomsByFloor: groupRoomsByFloor,
    getState: getState,
    saveState: saveState,
    startMode: startMode,
    maybeSetInitialMode: maybeSetInitialMode,
    canEnterFloor: canEnterFloor,
    canEnterRoom: canEnterRoom,
    roomById: roomById,
    getEventById: getEventById,
    requirementsMet: requirementsMet,
    getNextPhoneEvent: getNextPhoneEvent,
    startPhoneRinging: startPhoneRinging,
    cancelPhoneRinging: cancelPhoneRinging,
    acceptPhoneEvent: acceptPhoneEvent,
    finishPhoneEvent: finishPhoneEvent,
    completeScenarioEvent: completeScenarioEvent,
    completeEvent: completeScenarioEvent,
    getActiveRoomEvent: getActiveRoomEvent,
    getManagerEvent: getManagerEvent,
    setRoomEventActive: setRoomEventActive,
    getDiaryEntries: getDiaryEntries,
    markRoomEntered: markRoomEntered
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init, { once: true });
  } else {
    init();
  }
})();
