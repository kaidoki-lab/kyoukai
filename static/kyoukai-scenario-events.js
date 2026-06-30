(function () {
  "use strict";

  window.KYOUKAI_SCENARIO_EVENTS = {
    version: "scenario-mode-v1",
    phoneEvents: [
      {
        event_id: "phone_observation_001",
        caller: "observer",
        room: "observation",
        floor: null,
        priority: 10,
        requirements: [
          { type: "mode", value: "scenario" },
          { type: "event_not_completed", event_id: "phone_observation_001" }
        ],
        completed: false,
        next_events: [],
        route_id: "route_a",
        chapter_id: "chapter_001",
        conversation: [
          "赤い電話が鳴っている。",
          "観測室から、短い呼吸音だけが届いている。",
          "2階の観測室へ向かう必要がある。"
        ],
        effects: [
          { type: "set_phone_state", value: "answered" },
          { type: "set_current_event", event_id: "phone_observation_001" },
          { type: "set_room_state", room: "observation", state: "waiting" },
          { type: "unlock_room", room: "observation" },
          { type: "set_manager_state", state: "away" }
        ]
      }
    ],
    managerEvents: [],
    roomEvents: []
  };
})();
