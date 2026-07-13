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

  function getBaseRooms() {
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

  function getTopFloorRoom(baseRooms) {
    if (!building.topFloorRoom) return null;
    var rooms = Array.isArray(baseRooms) ? baseRooms : getBaseRooms();
    var maxBaseFloor = rooms.reduce(function (max, room) {
      return Math.max(max, room.floor);
    }, Number(building.initialScenarioFloors || 3));
    return Object.assign({}, building.topFloorRoom, {
      floor: maxBaseFloor + 1,
      slot: 1,
      roomIndex: null,
      topFloorOnly: true
    });
  }

  function getRooms() {
    var rooms = getBaseRooms();
    var topFloorRoom = getTopFloorRoom(rooms);
    return topFloorRoom ? rooms.concat([topFloorRoom]) : rooms;
  }

  function nextRoomIndex(rooms) {
    var list = (Array.isArray(rooms) ? rooms : getBaseRooms()).filter(function (room) {
      return !room.topFloorOnly;
    });
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
      if (room.topFloorOnly) {
        floors[floorKey] = [room];
      } else {
        floors[floorKey][room.slot - 1] = room;
      }
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
      event_completed_at: {},
      enabled_event_ids: [],
      room_states: roomStates,
      unlocked_floor_ids: defaultUnlockedFloorIds(),
      completed_scenario_count: 0,
      current_target_room_id: null,
      active_phone_event_id: null,
      phone_state: "idle",
      manager_state: "hidden",
      last_completed_event_id: null,
      last_phone_ring_at: null,
      phone_wait_started_at: null,
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
      final_route_available: false,
      top_floor_unlocked: false,
      annihilation_key_obtained: false,
      annihilation_key_obtained_at: null,
      annihilation_key_used: false,
      annihilation_key_used_at: null,
      annihilation_key_consumed: false,
      annihilation_key_obtain_lock: false,
      annihilation_key_use_lock: false,
      key_box_state: "contains_annihilation_key",
      top_floor_keyhole_active: false,
      top_floor_entered: false,
      top_floor_entered_at: null,
      top_floor_event_completed: false,
      top_floor_keyhole_completed: false,
      keyhole_state: "inactive",
      keyhole_touched: false,
      keyhole_touched_without_key: false,
      keyhole_interaction_lock: false,
      observer_final_mode: false,
      observer_final_event_started: false,
      observer_final_event_started_at: null,
      observer_final_event_completed: false,
      observer_final_event_completed_at: null,
      observer_reversed: false,
      final_text_12_displayed: false,
      return_control_unlocked: false,
      user_selected_manager_return: false,
      observer_final_transition_lock: false,
      observer_final_text_lock: false,
      observer_final_return_lock: false,
      route_e_stage: "not_started",
      route_e_started_at: null,
      route_e_phone_answered: false,
      route_e_phone_answered_at: null,
      route_e_phone_completed: false,
      route_e_phone_completed_at: null,
      route_e_phone_answer_lock: false,
      ending_completed: false,
      kyoukai_completed_at: null,
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
    next.event_completed_at = Object.assign({}, next.event_completed_at || {});
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
    next.final_route_available = Boolean(next.final_route_available);
    next.top_floor_unlocked = Boolean(next.top_floor_unlocked);
    next.annihilation_key_obtained = Boolean(next.annihilation_key_obtained);
    next.annihilation_key_used = Boolean(next.annihilation_key_used);
    next.annihilation_key_consumed = Boolean(next.annihilation_key_consumed);
    next.annihilation_key_obtain_lock = Boolean(next.annihilation_key_obtain_lock);
    next.annihilation_key_use_lock = Boolean(next.annihilation_key_use_lock);
    next.key_box_state = next.key_box_state || "contains_annihilation_key";
    if (next.annihilation_key_obtained === true) next.key_box_state = "empty";
    if (next.annihilation_key_used === true) next.annihilation_key_consumed = true;
    if (next.annihilation_key_consumed === true && Array.isArray(next.items)) {
      next.items = next.items.filter(function (item) { return item !== "annihilation_key"; });
    }
    next.top_floor_keyhole_active = Boolean(next.top_floor_keyhole_active);
    next.top_floor_entered = Boolean(next.top_floor_entered);
    next.top_floor_event_completed = Boolean(next.top_floor_event_completed);
    next.top_floor_keyhole_completed = Boolean(next.top_floor_keyhole_completed);
    next.keyhole_touched = Boolean(next.keyhole_touched);
    next.keyhole_touched_without_key = Boolean(next.keyhole_touched_without_key);
    next.keyhole_interaction_lock = Boolean(next.keyhole_interaction_lock);
    next.observer_final_mode = Boolean(next.observer_final_mode);
    next.observer_final_event_started = Boolean(next.observer_final_event_started);
    next.observer_final_event_completed = Boolean(next.observer_final_event_completed);
    next.observer_reversed = Boolean(next.observer_reversed);
    next.final_text_12_displayed = Boolean(next.final_text_12_displayed);
    next.return_control_unlocked = Boolean(next.return_control_unlocked);
    next.user_selected_manager_return = Boolean(next.user_selected_manager_return);
    next.observer_final_transition_lock = Boolean(next.observer_final_transition_lock);
    next.observer_final_text_lock = Boolean(next.observer_final_text_lock);
    next.observer_final_return_lock = Boolean(next.observer_final_return_lock);
    next.keyhole_state = next.keyhole_state || "inactive";
    if (next.keyhole_state === "processing" && next.top_floor_keyhole_completed !== true) {
      next.keyhole_state = hasAnnihilationKey(next) ? "ready" : "waiting_for_key";
      next.keyhole_interaction_lock = false;
      next.annihilation_key_use_lock = false;
      next.annihilation_key_used = false;
      next.annihilation_key_used_at = null;
      next.annihilation_key_consumed = false;
    }
    next.route_e_phone_answered = Boolean(next.route_e_phone_answered);
    next.route_e_phone_completed = Boolean(next.route_e_phone_completed);
    next.route_e_phone_answer_lock = Boolean(next.route_e_phone_answer_lock);
    next.ending_completed = Boolean(next.ending_completed);
    next.route_e_stage = next.route_e_stage || "not_started";

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
    var topFloorRoom = getTopFloorRoom();
    if (topFloorRoom && topFloorRoom.floor === number && state.top_floor_unlocked) return true;
    return ["unlocked", "completed"].indexOf(state.floor_state[key]) !== -1 || state.unlocked_floor_ids.indexOf(getFloorId(number)) !== -1;
  }

  function canEnterRoom(roomId) {
    var state = getState();
    if (state.mode !== "scenario") return true;
    var room = roomById(roomId);
    if (!room) return true;
    if (room.topFloorOnly) {
      return Boolean(state.top_floor_unlocked || state.unlocked_rooms.indexOf(roomId) !== -1);
    }
    if (!canEnterFloor(room.floor)) return false;
    var roomState = state.room_states[roomId] || room.defaultState || "normal";
    if (roomState === "disabled") return false;
    return [
      "normal",
      "waiting",
      "active",
      "completed",
      "post_route_a",
      "post_route_b",
      "post_route_c",
      "post_route_d",
      "signal_contaminated",
      "observation_signal_received",
      "unregistered_record_visible",
      "unregistered_record_deliberation",
      "unregistered_container_active",
      "persistent_fragment_visible",
      "route_c_conversation",
      "persistent_fragment_generation",
      "collective_reaction_ripple",
      "shared_reaction_attempt",
      "low_resolution_reaction",
      "reaction_amplified_by_repetition",
      "almost_speaking"
    ].indexOf(roomState) !== -1 || state.unlocked_rooms.indexOf(roomId) !== -1;
  }

  function hasAnnihilationKey(state) {
    var next = state || getState();
    if (next.annihilation_key_used === true || next.annihilation_key_consumed === true) return false;
    return Boolean(
      next.annihilation_key_obtained === true ||
      (Array.isArray(next.items) && next.items.indexOf("annihilation_key") !== -1)
    );
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
      if (requirement.type === "all_of") return requirementsMet(requirement.requirements || [], state, ctx);
      if (requirement.type === "any_of") {
        return (requirement.requirements || []).some(function (group) {
          return requirementsMet(Array.isArray(group) ? group : [group], state, ctx);
        });
      }
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
      if (requirement.type === "floor_unlocked") return state.unlocked_floor_ids.indexOf(requirement.floor_id) !== -1;
      if (requirement.type === "state_equals") return state[requirement.key] === requirement.value;
      if (requirement.type === "state_not_equals") return state[requirement.key] !== requirement.value;
      if (requirement.type === "counter_gte") return Number(state[requirement.counter_id] || 0) >= Number(requirement.value || 0);
      if (requirement.type === "room_stay_seconds") return compareSeconds(Number(ctx.roomStaySeconds || 0), requirement.operator || ">=", Number(requirement.value || 0));
      if (requirement.type === "room_entered") return state.room_entry_history.some(function (entry) { return entry.room_id === requirement.room_id; });
      if (requirement.type === "interaction_completed") return state.interaction_history.indexOf(requirement.target) !== -1 || ctx.interactionTarget === requirement.target;
      if (requirement.type === "sequence_finished") return state.sequence_history.indexOf(requirement.event_id) !== -1 || ctx.sequenceEventId === requirement.event_id;
      if (requirement.type === "room_entered_after_event") {
        return currentRoomId === requirement.room_id && state.last_completed_event_id === requirement.after_event_id;
      }
      if (requirement.type === "room_reentered_after_event") {
        var completedAt = Date.parse(state.event_completed_at[requirement.after_event_id] || "");
        if (!Number.isFinite(completedAt)) return false;
        return currentRoomId === requirement.room_id && state.room_entry_history.some(function (entry) {
          return entry.room_id === requirement.room_id && Date.parse(entry.at || "") > completedAt;
        });
      }
      return requirementWarn(requirement);
    });
  }

  function getNextPhoneEvent(context) {
    var state = getState();
    if (state.mode !== "scenario") return null;
    return (events.phoneEvents || []).filter(function (event) {
      if (state.enabled_event_ids.indexOf(event.event_id) === -1) return false;
      if (!requirementsMet(event.requirements, state, context || {})) return false;
      var retrySeconds = Number(event.phone_config && event.phone_config.retry_interval_seconds || 0);
      if (!retrySeconds || !state.last_phone_ring_at) return true;
      var elapsedMs = Date.now() - Date.parse(state.last_phone_ring_at);
      return !Number.isFinite(elapsedMs) || elapsedMs >= retrySeconds * 1000;
    }).sort(function (a, b) {
      return Number(b.priority || 0) - Number(a.priority || 0);
    })[0] || null;
  }

  function startPhoneWait() {
    var state = getState();
    if (state.mode !== "scenario") return state;
    if (!state.phone_wait_started_at) {
      state.phone_wait_started_at = new Date().toISOString();
      return saveState(state);
    }
    return state;
  }

  function getPhoneWaitSeconds() {
    var state = getState();
    if (!state.phone_wait_started_at) return 0;
    var elapsedMs = Date.now() - Date.parse(state.phone_wait_started_at);
    return Number.isFinite(elapsedMs) ? Math.max(0, elapsedMs / 1000) : 0;
  }

  function setEventStatus(state, eventId, status) {
    if (!eventId) return;
    state.event_status[eventId] = status;
    if (status === "enabled" && state.enabled_event_ids.indexOf(eventId) === -1) state.enabled_event_ids.push(eventId);
    if (status === "completed") {
      if (state.completed_events.indexOf(eventId) === -1) state.completed_events.push(eventId);
      state.event_completed_at[eventId] = new Date().toISOString();
    }
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
    else if (effect.type === "set_state_value") state[effect.key] = effect.value;
    else if (effect.type === "set_timestamp") state[effect.key] = new Date().toISOString();
    else if (effect.type === "add_item") {
      state.items = unique((state.items || []).concat([effect.item_id]));
    } else if (effect.type === "remove_item") {
      state.items = (state.items || []).filter(function (item) { return item !== effect.item_id; });
    }
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
    state.last_phone_ring_at = new Date().toISOString();
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
    if (Array.isArray(event.start_effects) && event.start_effects.length) {
      event.start_effects.every(function (effect) {
        return applyEffect(state, effect);
      });
    }
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
    state.phone_wait_started_at = null;
    return saveState(state);
  }

  function resetPhoneWait() {
    var state = getState();
    state.phone_wait_started_at = null;
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
        category: entry.route_id === "route_e" ? "Route_E" : entry.route_id === "route_d" ? "Route_D" : entry.route_id === "route_c" ? "Route_C" : entry.route_id === "route_b" ? "Route_B" : "Route_A",
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
    hasAnnihilationKey: hasAnnihilationKey,
    roomById: roomById,
    getEventById: getEventById,
    requirementsMet: requirementsMet,
    getNextPhoneEvent: getNextPhoneEvent,
    startPhoneWait: startPhoneWait,
    getPhoneWaitSeconds: getPhoneWaitSeconds,
    startPhoneRinging: startPhoneRinging,
    cancelPhoneRinging: cancelPhoneRinging,
    acceptPhoneEvent: acceptPhoneEvent,
    finishPhoneEvent: finishPhoneEvent,
    resetPhoneWait: resetPhoneWait,
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
