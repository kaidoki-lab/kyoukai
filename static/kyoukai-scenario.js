(function () {
  "use strict";

  var STORAGE_KEY = "kyoukai_scenario_state_v1";
  var building = window.KYOUKAI_BUILDING || { roomsPerFloor: 5, rooms: [], initialScenarioFloors: 3 };
  var events = window.KYOUKAI_SCENARIO_EVENTS || { phoneEvents: [], managerEvents: [], roomEvents: [] };
  var roomsPerFloor = Number(building.roomsPerFloor || 5);
  var passiveRooms = { home: true, elevator: true, floor: true };

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

  function createDefaultState() {
    return {
      mode: null,
      current_route: null,
      current_chapter: null,
      current_event: null,
      manager_state: "hidden",
      phone_state: "idle",
      room_state: defaultRoomStates(),
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

  function getState() {
    try {
      var saved = window.localStorage.getItem(STORAGE_KEY);
      if (!saved) return createDefaultState();
      return Object.assign(createDefaultState(), JSON.parse(saved));
    } catch (error) {
      return createDefaultState();
    }
  }

  function saveState(state) {
    var next = Object.assign(createDefaultState(), state || {});
    next.updated_at = new Date().toISOString();
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(next));
    document.dispatchEvent(new CustomEvent("kyoukai:scenario-state", { detail: next }));
    return next;
  }

  function startMode(mode) {
    var state = getState();
    if (state.mode) return state;
    state.mode = mode;
    if (mode === "scenario") {
      state.current_route = "route_a";
      state.current_chapter = "chapter_001";
      state.manager_state = "visible";
      state.floor_state = defaultFloorStates();
    }
    if (mode === "free") {
      getRooms().forEach(function (room) {
        state.unlocked_rooms.push(room.id);
        state.room_state[room.id] = state.room_state[room.id] === "disabled" ? "disabled" : "normal";
        state.floor_state[String(room.floor).padStart(2, "0")] = "unlocked";
      });
    }
    return saveState(state);
  }

  function maybeSetInitialMode(roomId) {
    var state = getState();
    if (state.mode || !roomId || passiveRooms[roomId]) return state;
    return startMode(roomId === "kanrinin" ? "scenario" : "free");
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
    var key = String(floorNumber).padStart(2, "0");
    return ["unlocked", "completed"].indexOf(state.floor_state[key]) !== -1;
  }

  function canEnterRoom(roomId) {
    var state = getState();
    if (state.mode !== "scenario") return true;
    var room = roomById(roomId);
    if (!room) return true;
    if (!canEnterFloor(room.floor)) return false;
    var roomState = state.room_state[roomId] || room.defaultState || "normal";
    return ["normal", "waiting", "active", "completed"].indexOf(roomState) !== -1 || state.unlocked_rooms.indexOf(roomId) !== -1;
  }

  function showNotice(message) {
    var event = new CustomEvent("kyoukai:scenario-notice", { detail: { message: message } });
    document.dispatchEvent(event);
    if (!event.defaultPrevented) {
      window.alert(message);
    }
  }

  function requirementsMet(requirements, state) {
    return (requirements || []).every(function (requirement) {
      if (requirement.type === "mode") return state.mode === requirement.value;
      if (requirement.type === "event_completed") return state.completed_events.indexOf(requirement.event_id) !== -1;
      if (requirement.type === "event_not_completed") return state.completed_events.indexOf(requirement.event_id) === -1;
      if (requirement.type === "room_state") return state.room_state[requirement.room] === requirement.state;
      if (requirement.type === "floor_state") return state.floor_state[String(requirement.floor).padStart(2, "0")] === requirement.state;
      return true;
    });
  }

  function getNextPhoneEvent() {
    var state = getState();
    if (state.mode !== "scenario") return null;
    return (events.phoneEvents || []).filter(function (event) {
      return requirementsMet(event.requirements, state);
    }).sort(function (a, b) {
      return Number(b.priority || 0) - Number(a.priority || 0);
    })[0] || null;
  }

  function applyEffect(state, effect) {
    if (effect.type === "set_phone_state") state.phone_state = effect.value;
    if (effect.type === "set_current_event") state.current_event = effect.event_id;
    if (effect.type === "set_manager_state") state.manager_state = effect.state;
    if (effect.type === "set_room_state") state.room_state[effect.room] = effect.state;
    if (effect.type === "unlock_room") {
      var room = roomById(effect.room);
      if (state.unlocked_rooms.indexOf(effect.room) === -1) state.unlocked_rooms.push(effect.room);
      if (room) state.floor_state[String(room.floor).padStart(2, "0")] = "unlocked";
    }
  }

  function acceptPhoneEvent(eventId) {
    var event = (events.phoneEvents || []).find(function (item) {
      return item.event_id === eventId;
    });
    if (!event) return getState();
    var state = getState();
    (event.effects || []).forEach(function (effect) {
      applyEffect(state, effect);
    });
    state.conversation_history.push({ event_id: event.event_id, caller: event.caller, lines: event.conversation || [], at: new Date().toISOString() });
    return saveState(state);
  }

  function completeEvent(eventId) {
    var state = getState();
    if (state.completed_events.indexOf(eventId) === -1) state.completed_events.push(eventId);
    if (state.current_event === eventId) state.current_event = null;
    state.progress_rate = Math.round((state.completed_events.length / Math.max(1, (events.phoneEvents || []).length)) * 100);
    return saveState(state);
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
    maybeSetInitialMode(window.KYOUKAI_ROOM);
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
    getNextPhoneEvent: getNextPhoneEvent,
    acceptPhoneEvent: acceptPhoneEvent,
    completeEvent: completeEvent
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init, { once: true });
  } else {
    init();
  }
})();
