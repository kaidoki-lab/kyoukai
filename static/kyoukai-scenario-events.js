(function () {
  "use strict";

  var routeA = {
    schema_version: 1,
    route_id: "route_a",
    name: "混線している観測",
    type: "normal",
    theme: "観測域と受信域の間に発生した正体不明の混線",
    status_default: "not_started",
    shared_room_ids: ["kanrinin"],
    reserved_room_ids: ["observation", "signal"],
    start_requirements: [
      { type: "mode_equals", value: "scenario" },
      { type: "first_room_equals", room_id: "kanrinin" },
      { type: "route_status_equals", route_id: "route_a", value: "not_started" },
      { type: "active_route_equals", value: null }
    ],
    completion_requirements: [
      { type: "event_completed", event_id: "route_a_phone_001" },
      { type: "event_completed", event_id: "route_a_room_observation_001" },
      { type: "event_completed", event_id: "route_a_room_signal_001" },
      { type: "event_completed", event_id: "route_a_manager_return_001" }
    ],
    failure_requirements: []
  };

  var routeB = {
    schema_version: 1,
    route_id: "route_b",
    name: "記録されていない人",
    type: "normal",
    theme: "台帳に存在しない記録の保管先を確認する通常シナリオ",
    status_default: "not_started",
    shared_room_ids: ["kanrinin"],
    reserved_room_ids: ["archive", "hyougi", "gokuraku"],
    start_requirements: [
      { type: "mode_equals", value: "scenario" },
      { type: "route_status_equals", route_id: "route_a", value: "completed" },
      { type: "route_status_equals", route_id: "route_b", value: "not_started" },
      { type: "active_route_equals", value: null },
      { type: "floor_unlocked", floor_id: "floor_04" }
    ],
    completion_requirements: [
      { type: "event_completed", event_id: "route_b_phone_001" },
      { type: "event_completed", event_id: "route_b_room_archive_001" },
      { type: "event_completed", event_id: "route_b_room_hyougi_001" },
      { type: "event_completed", event_id: "route_b_room_gokuraku_001" },
      { type: "event_completed", event_id: "route_b_manager_return_001" }
    ],
    failure_requirements: []
  };

  var routeC = {
    schema_version: 1,
    route_id: "route_c",
    name: "壊れる前の形",
    type: "normal",
    theme: "崩壊と生成の境界",
    status_default: "not_started",
    shared_room_ids: ["kanrinin"],
    reserved_room_ids: ["null", "ma", "particles"],
    start_requirements: [
      { type: "mode_equals", value: "scenario" },
      { type: "route_status_equals", route_id: "route_a", value: "completed" },
      { type: "route_status_equals", route_id: "route_b", value: "completed" },
      { type: "route_status_equals", route_id: "route_c", value: "not_started" },
      { type: "active_route_equals", value: null },
      { type: "floor_unlocked", floor_id: "floor_05" }
    ],
    completion_requirements: [
      { type: "event_completed", event_id: "route_c_phone_001" },
      { type: "event_completed", event_id: "route_c_room_null_001" },
      { type: "event_completed", event_id: "route_c_room_ma_001" },
      { type: "event_completed", event_id: "route_c_room_particles_001" },
      { type: "event_completed", event_id: "route_c_manager_return_001" }
    ],
    failure_requirements: []
  };

  var routeD = {
    schema_version: 1,
    route_id: "route_d",
    name: "集まっているもの",
    type: "normal",
    theme: "単品では意味不明なものが、集まると別の反応になる",
    status_default: "not_started",
    shared_room_ids: ["kanrinin"],
    reserved_room_ids: ["ripple", "colony", "dot-art", "matsuri", "namahage"],
    start_requirements: [
      { type: "mode_equals", value: "scenario" },
      { type: "route_status_equals", route_id: "route_a", value: "completed" },
      { type: "route_status_equals", route_id: "route_b", value: "completed" },
      { type: "route_status_equals", route_id: "route_c", value: "completed" },
      { type: "route_status_equals", route_id: "route_d", value: "not_started" },
      { type: "active_route_equals", value: null },
      { type: "floor_unlocked", floor_id: "floor_06" }
    ],
    completion_requirements: [
      { type: "event_completed", event_id: "route_d_phone_001" },
      { type: "event_completed", event_id: "route_d_room_ripple_001" },
      { type: "event_completed", event_id: "route_d_room_colony_001" },
      { type: "event_completed", event_id: "route_d_room_dot_art_001" },
      { type: "event_completed", event_id: "route_d_room_matsuri_001" },
      { type: "event_completed", event_id: "route_d_room_namahage_001" },
      { type: "event_completed", event_id: "route_d_manager_return_001" }
    ],
    failure_requirements: []
  };

  var routeE = {
    schema_version: 1,
    route_id: "route_e",
    name: "観測の完了",
    type: "final",
    is_final_route: true,
    theme: "観測する側と観測される側の記録が揃い、観測が完了する",
    status_default: "not_started",
    shared_room_ids: ["kanrinin"],
    reserved_room_ids: ["top-floor", "observer"],
    start_requirements: [
      { type: "mode_equals", value: "scenario" },
      { type: "route_status_equals", route_id: "route_a", value: "completed" },
      { type: "route_status_equals", route_id: "route_b", value: "completed" },
      { type: "route_status_equals", route_id: "route_c", value: "completed" },
      { type: "route_status_equals", route_id: "route_d", value: "completed" },
      { type: "state_equals", key: "final_route_available", value: true },
      { type: "state_not_equals", key: "ending_completed", value: true },
      { type: "route_status_equals", route_id: "route_e", value: "available" },
      { type: "active_route_equals", value: null }
    ],
    completion_requirements: [
      { type: "event_completed", event_id: "route_e_phone_001" },
      { type: "event_completed", event_id: "route_e_top_floor_001" },
      { type: "event_completed", event_id: "route_e_annihilation_key_001" },
      { type: "event_completed", event_id: "route_e_observer_final_001" },
      { type: "event_completed", event_id: "route_e_manager_return_001" },
      { type: "event_completed", event_id: "route_e_final_diary_001" }
    ],
    failure_requirements: []
  };

  window.KYOUKAI_SCENARIO_EVENTS = {
    version: "route-e-foundation-v1",
    routes: [routeA, routeB, routeC, routeD, routeE],
    phoneEvents: [
      {
        event_id: "route_a_phone_001",
        route_id: "route_a",
        caller_id: "resident_observation_001",
        caller_display_name: "観測中のもの",
        caller: "観測中のもの",
        room: "observation",
        floor: null,
        priority: 10,
        requirements: [
          { type: "mode_equals", value: "scenario" },
          { type: "first_room_equals", room_id: "kanrinin" },
          { type: "route_status_equals", route_id: "route_a", value: "not_started" },
          { type: "room_stay_seconds", room_id: "kanrinin", operator: ">=", value: 20 },
          { type: "active_phone_event_equals", value: null },
          { type: "event_not_completed", event_id: "route_a_phone_001" }
        ],
        phone_config: {
          ring_audio: "/static/audio/kanrinin/red-phone-ring.mp3",
          retry_enabled: true,
          retry_trigger: "kanrinin_reentry",
          retry_interval_seconds: 60
        },
        conversation: [
          { speaker: "caller", text: "……聞こえますか。" },
          { speaker: "caller", text: "こちらを見ている画面に、知らないものが映っています。" },
          { speaker: "caller", text: "私ではありません。" },
          { speaker: "caller", text: "音は、下ではなく、別の部屋から来ています。" },
          { speaker: "caller", text: "先に、こちらを見てください。" },
          { speaker: "caller", text: "切れたあとも、音が残ります。" }
        ],
        effects: [
          { type: "set_route_status", route_id: "route_a", value: "active" },
          { type: "set_active_route", route_id: "route_a" },
          { type: "complete_event", event_id: "route_a_phone_001" },
          { type: "enable_event", event_id: "route_a_room_observation_001" },
          { type: "set_target_room", room_id: "observation" },
          { type: "append_diary_entry", entry_id: "route_a_diary_001" }
        ],
        next_events: ["route_a_room_observation_001"]
      },
      {
        event_id: "route_b_phone_001",
        route_id: "route_b",
        caller_id: "resident_unregistered_record_001",
        caller_display_name: "記録なし",
        caller: "記録なし",
        room: "archive",
        floor: null,
        priority: 10,
        requirements: [
          { type: "mode_equals", value: "scenario" },
          { type: "route_status_equals", route_id: "route_a", value: "completed" },
          { type: "route_status_equals", route_id: "route_b", value: "not_started" },
          { type: "active_route_equals", value: null },
          { type: "floor_unlocked", floor_id: "floor_04" },
          { type: "room_stay_seconds", room_id: "kanrinin", operator: ">=", value: 20 },
          { type: "active_phone_event_equals", value: null },
          { type: "event_enabled", event_id: "route_b_phone_001" },
          { type: "event_not_completed", event_id: "route_b_phone_001" }
        ],
        phone_config: {
          ring_audio: "/static/audio/kanrinin/red-phone-ring.mp3",
          retry_enabled: true,
          retry_trigger: "kanrinin_reentry",
          retry_interval_seconds: 60
        },
        caller_profile: {
          resident_type: "unregistered_record",
          home_room_id: null,
          identity_confirmed: false,
          resident_number: null,
          registered: false
        },
        conversation: [
          { speaker: "caller", text: "管理人室ですか。" },
          { speaker: "caller", text: "私の記録が、そちらに届いていません。" },
          { speaker: "caller", text: "名前はありません。" },
          { speaker: "caller", text: "名前がないのではなく、名前の欄そのものがありません。" },
          { speaker: "caller", text: "残っているものを確認してください。" },
          { speaker: "caller", text: "捨てられていなければ、まだ続いています。" }
        ],
        effects: [
          { type: "set_route_status", route_id: "route_b", value: "active" },
          { type: "set_active_route", route_id: "route_b" },
          { type: "complete_event", event_id: "route_b_phone_001" },
          { type: "enable_event", event_id: "route_b_room_archive_001" },
          { type: "set_target_room", room_id: "archive" },
          { type: "append_diary_entry", entry_id: "route_b_diary_001" }
        ],
        next_events: ["route_b_room_archive_001"]
      },
      {
        event_id: "route_c_phone_001",
        route_id: "route_c",
        caller_id: "resident_null_fragment_001",
        caller_display_name: "発信元不明",
        caller: "発信元不明",
        room: "null",
        floor: null,
        priority: 10,
        requirements: [
          { type: "mode_equals", value: "scenario" },
          { type: "route_status_equals", route_id: "route_a", value: "completed" },
          { type: "route_status_equals", route_id: "route_b", value: "completed" },
          { type: "route_status_equals", route_id: "route_c", value: "not_started" },
          { type: "active_route_equals", value: null },
          { type: "floor_unlocked", floor_id: "floor_05" },
          { type: "room_stay_seconds", room_id: "kanrinin", operator: ">=", value: 20 },
          { type: "room_reentered_after_event", room_id: "kanrinin", after_event_id: "route_b_manager_return_001" },
          { type: "active_phone_event_equals", value: null },
          { type: "event_enabled", event_id: "route_c_phone_001" },
          { type: "event_not_completed", event_id: "route_c_phone_001" }
        ],
        phone_config: {
          ring_audio: "/static/audio/kanrinin/red-phone-ring.mp3",
          retry_enabled: true,
          retry_trigger: "kanrinin_reentry",
          retry_interval_seconds: 60
        },
        caller_profile: {
          resident_type: "unknown_source",
          home_room_id: null,
          identity_confirmed: false,
          resident_number: null,
          registered: false
        },
        conversation: [
          { speaker: "caller", text: "崩れる音。" },
          { speaker: "caller", text: "一定の間隔で、硬いものが接触する音。" },
          { speaker: "caller", text: "まだ" },
          { speaker: "caller", text: "形が" },
          { speaker: "caller", text: "残っています" }
        ],
        effects: [
          { type: "set_route_status", route_id: "route_c", value: "active" },
          { type: "set_active_route", route_id: "route_c" },
          { type: "complete_event", event_id: "route_c_phone_001" },
          { type: "enable_event", event_id: "route_c_room_null_001" },
          { type: "set_target_room", room_id: "null" },
          { type: "append_diary_entry", entry_id: "route_c_diary_001" }
        ],
        next_events: ["route_c_room_null_001"]
      },
      {
        event_id: "route_d_phone_001",
        route_id: "route_d",
        caller_id: "resident_collective_reaction_001",
        caller_display_name: "複数",
        caller: "複数",
        room: "ripple",
        floor: null,
        priority: 10,
        requirements: [
          { type: "mode_equals", value: "scenario" },
          { type: "route_status_equals", route_id: "route_a", value: "completed" },
          { type: "route_status_equals", route_id: "route_b", value: "completed" },
          { type: "route_status_equals", route_id: "route_c", value: "completed" },
          { type: "route_status_equals", route_id: "route_d", value: "not_started" },
          { type: "active_route_equals", value: null },
          { type: "floor_unlocked", floor_id: "floor_06" },
          { type: "room_stay_seconds", room_id: "kanrinin", operator: ">=", value: 20 },
          { type: "room_reentered_after_event", room_id: "kanrinin", after_event_id: "route_c_manager_return_001" },
          { type: "active_phone_event_equals", value: null },
          { type: "event_not_completed", event_id: "route_d_phone_001" }
        ],
        phone_config: {
          ring_audio: "/static/audio/kanrinin/red-phone-ring.mp3",
          retry_enabled: true,
          retry_trigger: "kanrinin_reentry",
          retry_interval_seconds: 60
        },
        caller_profile: {
          resident_type: "collective_reaction",
          home_room_id: null,
          identity_confirmed: false,
          resident_number: null,
          registered: false
        },
        conversation: [
          { speaker: "caller", text: "……あ" },
          { speaker: "caller", text: "……い" },
          { speaker: "caller", text: "違う" },
          { speaker: "caller", text: "まだ" },
          { speaker: "caller", text: "声では" },
          { speaker: "caller", text: "集めて" },
          { speaker: "caller", text: "聞こえる形に" }
        ],
        effects: [
          { type: "set_route_status", route_id: "route_d", value: "active" },
          { type: "set_active_route", route_id: "route_d" },
          { type: "complete_event", event_id: "route_d_phone_001" },
          { type: "enable_event", event_id: "route_d_room_ripple_001" },
          { type: "set_target_room", room_id: "ripple" },
          { type: "append_diary_entry", entry_id: "route_d_diary_001" }
        ],
        next_events: ["route_d_room_ripple_001"]
      },
      {
        event_id: "route_e_phone_001",
        route_id: "route_e",
        caller_id: "route_e_caller_001",
        caller_display_name: "記録なし",
        caller: "記録なし",
        room: "kanrinin",
        floor: null,
        priority: 100,
        requirements: [
          { type: "mode_equals", value: "scenario" },
          { type: "route_status_equals", route_id: "route_a", value: "completed" },
          { type: "route_status_equals", route_id: "route_b", value: "completed" },
          { type: "route_status_equals", route_id: "route_c", value: "completed" },
          { type: "route_status_equals", route_id: "route_d", value: "completed" },
          { type: "state_equals", key: "final_route_available", value: true },
          { type: "state_not_equals", key: "ending_completed", value: true },
          { type: "state_not_equals", key: "route_e_phone_completed", value: true },
          { type: "active_phone_event_equals", value: null },
          { type: "event_enabled", event_id: "route_e_phone_001" },
          { type: "event_not_completed", event_id: "route_e_phone_complete_001" },
          {
            type: "any_of",
            requirements: [
              [
                { type: "route_status_equals", route_id: "route_e", value: "available" },
                { type: "active_route_equals", value: null },
                { type: "room_reentered_after_event", room_id: "kanrinin", after_event_id: "route_d_manager_return_001" },
                { type: "room_stay_seconds", room_id: "kanrinin", operator: ">=", value: 20 }
              ],
              [
                { type: "route_status_equals", route_id: "route_e", value: "active" },
                { type: "active_route_equals", value: "route_e" },
                { type: "room_stay_seconds", room_id: "kanrinin", operator: ">=", value: 1.5 }
              ]
            ]
          }
        ],
        phone_config: {
          ring_audio: "/static/audio/kanrinin/red-phone-ring.mp3",
          retry_enabled: true,
          retry_trigger: "kanrinin_reentry",
          retry_interval_seconds: 3,
          dialogue_mode: "manual",
          character_interval_ms: 45,
          resume_ring_delay_ms: 1500
        },
        caller_profile: {
          resident_type: "unknown_record",
          identity_confirmed: false,
          registered: false
        },
        conversation: [
          { id: "route_e_phone_line_001", speaker: "記録なし", text: "聞こえています。" },
          { id: "route_e_phone_line_002", speaker: "記録なし", text: "四つの記録を確認しました。" },
          { id: "route_e_phone_line_003", speaker: "記録なし", text: "受信。\n保管。\n生成。\n集合。" },
          { id: "route_e_phone_line_004", speaker: "記録なし", text: "あなたが触れたものは、\nすべて次の形に移されています。" },
          { id: "route_e_phone_line_005", speaker: "記録なし", text: "これ以上、\n下の階で確認するものはありません。" },
          { id: "route_e_phone_line_006", speaker: "記録なし", text: "最上階を開きました。" },
          { id: "route_e_phone_line_007", speaker: "記録なし", text: "鍵は、\n最初から管理人室にあります。" },
          { id: "route_e_phone_line_008", speaker: "記録なし", text: "持ってきてください。" },
          { id: "route_e_phone_line_009", speaker: "記録なし", text: "最後に確認するのは、\nあなたが見ていたものではありません。" },
          { id: "route_e_phone_line_010", speaker: "記録なし", text: "通話を終了します。" }
        ],
        start_effects: [
          { type: "set_route_status", route_id: "route_e", value: "active" },
          { type: "set_active_route", route_id: "route_e" },
          { type: "set_state_value", key: "route_e_stage", value: "route_e_phone_active" },
          { type: "set_timestamp", key: "route_e_started_at" },
          { type: "set_state_value", key: "route_e_phone_answered", value: true },
          { type: "set_timestamp", key: "route_e_phone_answered_at" },
          { type: "set_state_value", key: "route_e_phone_completed", value: false },
          { type: "set_state_value", key: "top_floor_unlocked", value: false },
          { type: "set_state_value", key: "route_e_phone_answer_lock", value: true },
          { type: "complete_event", event_id: "route_e_phone_answer_001" }
        ],
        effects: [
          { type: "complete_event", event_id: "route_e_phone_dialogue_001" },
          { type: "complete_event", event_id: "route_e_phone_complete_001" },
          { type: "complete_event", event_id: "route_e_phone_001" },
          { type: "set_route_status", route_id: "route_e", value: "active" },
          { type: "set_active_route", route_id: "route_e" },
          { type: "set_state_value", key: "route_e_stage", value: "route_e_top_floor_unlocked" },
          { type: "set_state_value", key: "route_e_phone_completed", value: true },
          { type: "set_timestamp", key: "route_e_phone_completed_at" },
          { type: "set_state_value", key: "top_floor_unlocked", value: true },
          { type: "set_state_value", key: "top_floor_keyhole_active", value: false },
          { type: "set_state_value", key: "route_e_phone_answer_lock", value: false },
          { type: "enable_event", event_id: "route_e_annihilation_key_available_001" },
          { type: "enable_event", event_id: "route_e_top_floor_001" },
          { type: "set_target_room", room_id: "top-floor" }
        ],
        next_events: ["route_e_top_floor_001"]
      }
    ],
    roomEvents: [
      {
        event_id: "route_e_annihilation_key_available_001",
        route_id: "route_e",
        room_id: "kanrinin",
        requirements: [
          { type: "mode_equals", value: "scenario" },
          { type: "route_status_equals", route_id: "route_e", value: "active" },
          { type: "active_route_equals", value: "route_e" },
          { type: "state_equals", key: "route_e_phone_completed", value: true },
          { type: "state_not_equals", key: "ending_completed", value: true },
          { type: "state_not_equals", key: "annihilation_key_obtained", value: true }
        ],
        effects: []
      },
      {
        event_id: "route_e_annihilation_key_obtain_001",
        route_id: "route_e",
        room_id: "kanrinin",
        requirements: [
          { type: "mode_equals", value: "scenario" },
          { type: "route_status_equals", route_id: "route_e", value: "active" },
          { type: "active_route_equals", value: "route_e" },
          { type: "state_equals", key: "route_e_phone_completed", value: true },
          { type: "state_not_equals", key: "ending_completed", value: true },
          { type: "state_not_equals", key: "annihilation_key_obtained", value: true },
          { type: "interaction_completed", target: "annihilation-key" }
        ],
        effects: [
          { type: "complete_event", event_id: "route_e_annihilation_key_obtain_001" },
          { type: "set_state_value", key: "annihilation_key_obtained", value: true },
          { type: "set_timestamp", key: "annihilation_key_obtained_at" },
          { type: "set_state_value", key: "annihilation_key_used", value: false },
          { type: "set_state_value", key: "annihilation_key_consumed", value: false },
          { type: "set_state_value", key: "annihilation_key_obtain_lock", value: false },
          { type: "set_state_value", key: "route_e_stage", value: "annihilation_key_obtained" },
          { type: "set_state_value", key: "key_box_state", value: "empty" },
          { type: "add_item", item_id: "annihilation_key" },
          { type: "enable_event", event_id: "route_e_annihilation_key_ready_001" }
        ]
      },
      {
        event_id: "route_e_annihilation_key_box_empty_001",
        route_id: "route_e",
        room_id: "kanrinin",
        requirements: [
          { type: "state_equals", key: "key_box_state", value: "empty" }
        ],
        effects: []
      },
      {
        event_id: "route_e_top_floor_unlock_001",
        route_id: "route_e",
        room_id: "top-floor",
        requirements: [
          { type: "mode_equals", value: "scenario" },
          { type: "route_status_equals", route_id: "route_e", value: "active" },
          { type: "active_route_equals", value: "route_e" },
          { type: "state_equals", key: "route_e_phone_completed", value: true },
          { type: "state_equals", key: "top_floor_unlocked", value: true },
          { type: "state_not_equals", key: "ending_completed", value: true }
        ],
        effects: []
      },
      {
        event_id: "route_e_top_floor_enter_001",
        route_id: "route_e",
        room_id: "top-floor",
        requirements: [
          { type: "mode_equals", value: "scenario" },
          { type: "route_status_equals", route_id: "route_e", value: "active" },
          { type: "active_route_equals", value: "route_e" },
          { type: "state_equals", key: "route_e_phone_completed", value: true },
          { type: "state_equals", key: "top_floor_unlocked", value: true },
          { type: "state_not_equals", key: "ending_completed", value: true },
          { type: "event_not_completed", event_id: "route_e_top_floor_enter_001" }
        ],
        effects: [
          { type: "complete_event", event_id: "route_e_top_floor_enter_001" },
          { type: "set_state_value", key: "top_floor_entered", value: true },
          { type: "set_timestamp", key: "top_floor_entered_at" },
          { type: "set_state_value", key: "route_e_stage", value: "top_floor_entered" },
          { type: "set_state_value", key: "top_floor_keyhole_active", value: true }
        ]
      },
      {
        event_id: "route_e_keyhole_available_001",
        route_id: "route_e",
        room_id: "top-floor",
        requirements: [
          { type: "state_equals", key: "top_floor_entered", value: true },
          { type: "state_not_equals", key: "top_floor_keyhole_completed", value: true }
        ],
        effects: []
      },
      {
        event_id: "route_e_keyhole_touch_without_key_001",
        route_id: "route_e",
        room_id: "top-floor",
        requirements: [
          { type: "state_equals", key: "top_floor_entered", value: true },
          { type: "state_not_equals", key: "top_floor_keyhole_completed", value: true }
        ],
        effects: [
          { type: "complete_event", event_id: "route_e_keyhole_touch_without_key_001" },
          { type: "set_state_value", key: "keyhole_touched", value: true },
          { type: "set_state_value", key: "keyhole_touched_without_key", value: true },
          { type: "set_state_value", key: "keyhole_state", value: "waiting_for_key" }
        ]
      },
      {
        event_id: "route_e_keyhole_ready_001",
        route_id: "route_e",
        room_id: "top-floor",
        requirements: [
          { type: "state_equals", key: "top_floor_entered", value: true },
          { type: "state_not_equals", key: "top_floor_keyhole_completed", value: true }
        ],
        effects: [
          { type: "set_state_value", key: "keyhole_state", value: "ready" }
        ]
      },
      {
        event_id: "route_e_annihilation_key_ready_001",
        route_id: "route_e",
        room_id: "top-floor",
        requirements: [
          { type: "mode_equals", value: "scenario" },
          { type: "route_status_equals", route_id: "route_e", value: "active" },
          { type: "active_route_equals", value: "route_e" },
          { type: "state_equals", key: "route_e_phone_completed", value: true },
          { type: "state_equals", key: "top_floor_unlocked", value: true },
          { type: "state_equals", key: "top_floor_entered", value: true },
          { type: "state_equals", key: "annihilation_key_obtained", value: true },
          { type: "state_not_equals", key: "annihilation_key_used", value: true },
          { type: "state_not_equals", key: "top_floor_keyhole_completed", value: true },
          { type: "state_not_equals", key: "ending_completed", value: true }
        ],
        effects: [
          { type: "set_state_value", key: "keyhole_state", value: "ready" }
        ]
      },
      {
        event_id: "route_e_keyhole_processing_001",
        route_id: "route_e",
        room_id: "top-floor",
        requirements: [
          { type: "state_equals", key: "keyhole_state", value: "ready" },
          { type: "state_not_equals", key: "top_floor_keyhole_completed", value: true }
        ],
        effects: []
      },
      {
        event_id: "route_e_annihilation_key_insert_001",
        route_id: "route_e",
        room_id: "top-floor",
        requirements: [
          { type: "state_equals", key: "keyhole_state", value: "ready" },
          { type: "state_equals", key: "annihilation_key_obtained", value: true },
          { type: "state_not_equals", key: "annihilation_key_used", value: true },
          { type: "state_not_equals", key: "top_floor_keyhole_completed", value: true }
        ],
        effects: [
          { type: "complete_event", event_id: "route_e_annihilation_key_insert_001" },
          { type: "set_state_value", key: "keyhole_state", value: "processing" },
          { type: "set_state_value", key: "annihilation_key_use_lock", value: true }
        ]
      },
      {
        event_id: "route_e_annihilation_key_turn_001",
        route_id: "route_e",
        room_id: "top-floor",
        requirements: [
          { type: "state_equals", key: "keyhole_state", value: "processing" },
          { type: "state_equals", key: "annihilation_key_obtained", value: true },
          { type: "state_not_equals", key: "top_floor_keyhole_completed", value: true }
        ],
        effects: [
          { type: "complete_event", event_id: "route_e_annihilation_key_turn_001" }
        ]
      },
      {
        event_id: "route_e_annihilation_key_use_001",
        route_id: "route_e",
        room_id: "top-floor",
        requirements: [
          { type: "state_equals", key: "keyhole_state", value: "processing" },
          { type: "state_equals", key: "annihilation_key_obtained", value: true },
          { type: "state_not_equals", key: "annihilation_key_used", value: true },
          { type: "state_not_equals", key: "top_floor_keyhole_completed", value: true }
        ],
        effects: [
          { type: "complete_event", event_id: "route_e_annihilation_key_use_001" },
          { type: "set_state_value", key: "annihilation_key_used", value: true },
          { type: "set_timestamp", key: "annihilation_key_used_at" },
          { type: "set_state_value", key: "annihilation_key_consumed", value: true },
          { type: "remove_item", item_id: "annihilation_key" }
        ]
      },
      {
        event_id: "route_e_annihilation_key_complete_001",
        route_id: "route_e",
        room_id: "top-floor",
        requirements: [
          { type: "state_equals", key: "annihilation_key_used", value: true },
          { type: "state_equals", key: "annihilation_key_consumed", value: true },
          { type: "state_not_equals", key: "ending_completed", value: true }
        ],
        effects: [
          { type: "complete_event", event_id: "route_e_annihilation_key_complete_001" },
          { type: "complete_event", event_id: "route_e_annihilation_key_001" },
          { type: "complete_event", event_id: "route_e_top_floor_001" },
          { type: "complete_event", event_id: "route_e_keyhole_complete_001" },
          { type: "set_state_value", key: "top_floor_keyhole_completed", value: true },
          { type: "set_state_value", key: "top_floor_event_completed", value: true },
          { type: "set_state_value", key: "keyhole_state", value: "completed" },
          { type: "set_state_value", key: "annihilation_key_use_lock", value: false },
          { type: "set_state_value", key: "route_e_stage", value: "keyhole_completed" },
          { type: "enable_event", event_id: "route_e_observer_transition_001" },
          { type: "set_target_room", room_id: "observer" }
        ],
        next_events: ["route_e_observer_final_001"]
      },
      {
        event_id: "route_e_observer_transition_001",
        route_id: "route_e",
        room_id: "top-floor",
        requirements: [
          { type: "mode_equals", value: "scenario" },
          { type: "route_status_equals", route_id: "route_e", value: "active" },
          { type: "active_route_equals", value: "route_e" },
          { type: "state_equals", key: "annihilation_key_used", value: true },
          { type: "state_equals", key: "top_floor_keyhole_completed", value: true },
          { type: "state_equals", key: "top_floor_event_completed", value: true },
          { type: "state_not_equals", key: "observer_final_event_completed", value: true },
          { type: "state_not_equals", key: "ending_completed", value: true }
        ],
        effects: [
          { type: "complete_event", event_id: "route_e_observer_transition_001" },
          { type: "set_state_value", key: "observer_final_mode", value: true },
          { type: "set_state_value", key: "observer_final_transition_lock", value: false },
          { type: "set_state_value", key: "route_e_stage", value: "observer_transition" },
          { type: "set_target_room", room_id: "observer" }
        ],
        next_events: ["route_e_observer_enter_001"]
      },
      {
        event_id: "route_e_observer_enter_001",
        route_id: "route_e",
        room_id: "observer",
        requirements: [
          { type: "mode_equals", value: "scenario" },
          { type: "route_status_equals", route_id: "route_e", value: "active" },
          { type: "active_route_equals", value: "route_e" },
          { type: "state_equals", key: "annihilation_key_used", value: true },
          { type: "state_equals", key: "top_floor_keyhole_completed", value: true },
          { type: "state_not_equals", key: "observer_final_event_completed", value: true },
          { type: "state_not_equals", key: "ending_completed", value: true }
        ],
        effects: [
          { type: "complete_event", event_id: "route_e_observer_enter_001" },
          { type: "set_state_value", key: "observer_final_mode", value: true },
          { type: "set_state_value", key: "observer_final_event_started", value: true },
          { type: "set_timestamp", key: "observer_final_event_started_at" },
          { type: "set_state_value", key: "route_e_stage", value: "observer_active" }
        ],
        next_events: ["route_e_observer_text_001"]
      },
      {
        event_id: "route_e_observer_text_001",
        route_id: "route_e",
        room_id: "observer",
        requirements: [
          { type: "state_equals", key: "observer_final_event_started", value: true },
          { type: "state_not_equals", key: "observer_final_event_completed", value: true },
          { type: "state_not_equals", key: "ending_completed", value: true }
        ],
        effects: [
          { type: "complete_event", event_id: "route_e_observer_text_001" },
          { type: "set_state_value", key: "final_text_12_displayed", value: true },
          { type: "set_state_value", key: "return_control_unlocked", value: true },
          { type: "set_state_value", key: "observer_final_text_lock", value: false }
        ]
      },
      {
        event_id: "route_e_observer_reverse_001",
        route_id: "route_e",
        room_id: "observer",
        requirements: [
          { type: "state_equals", key: "return_control_unlocked", value: true },
          { type: "state_not_equals", key: "observer_final_event_completed", value: true },
          { type: "state_not_equals", key: "ending_completed", value: true }
        ],
        effects: [
          { type: "complete_event", event_id: "route_e_observer_reverse_001" },
          { type: "set_state_value", key: "observer_reversed", value: true },
          { type: "set_state_value", key: "user_selected_manager_return", value: true }
        ]
      },
      {
        event_id: "route_e_observer_complete_001",
        route_id: "route_e",
        room_id: "observer",
        requirements: [
          { type: "state_equals", key: "observer_reversed", value: true },
          { type: "state_equals", key: "user_selected_manager_return", value: true },
          { type: "state_not_equals", key: "observer_final_event_completed", value: true },
          { type: "state_not_equals", key: "ending_completed", value: true }
        ],
        effects: [
          { type: "complete_event", event_id: "route_e_observer_complete_001" },
          { type: "complete_event", event_id: "route_e_observer_final_001" },
          { type: "complete_event", event_id: "route_e_manager_return_001" },
          { type: "set_state_value", key: "observer_final_event_completed", value: true },
          { type: "set_timestamp", key: "observer_final_event_completed_at" },
          { type: "set_state_value", key: "observer_final_return_lock", value: false },
          { type: "set_state_value", key: "route_e_stage", value: "manager_return" },
          { type: "set_target_room", room_id: "kanrinin" }
        ],
        next_events: ["route_e_final_diary_001"]
      },
      {
        event_id: "route_e_keyhole_complete_001",
        route_id: "route_e",
        room_id: "top-floor",
        requirements: [
          { type: "state_equals", key: "top_floor_keyhole_completed", value: true }
        ],
        effects: []
      },
      {
        event_id: "route_a_room_observation_001",
        route_id: "route_a",
        room_id: "observation",
        requirements: [
          { type: "route_status_equals", route_id: "route_a", value: "active" },
          { type: "event_completed", event_id: "route_a_phone_001" },
          { type: "event_enabled", event_id: "route_a_room_observation_001" },
          { type: "event_not_completed", event_id: "route_a_room_observation_001" }
        ],
        room_state_before: "normal",
        room_state_during: "signal_contaminated",
        room_state_after: "post_route_a",
        messages: [
          "これは、こちらの観測ではありません。",
          "画面の奥に、もう一つ反応があります。",
          "音がする部屋を確認してください。"
        ],
        interaction: { target: "observation-primary", action: "activate", repeatable: false },
        completion_requirements: [
          { type: "room_entered", room_id: "observation" },
          { type: "interaction_completed", target: "observation-primary" },
          { type: "sequence_finished", event_id: "route_a_room_observation_001" }
        ],
        effects: [
          { type: "complete_event", event_id: "route_a_room_observation_001" },
          { type: "set_room_state", room_id: "observation", value: "post_route_a" },
          { type: "enable_event", event_id: "route_a_room_signal_001" },
          { type: "set_target_room", room_id: "signal" },
          { type: "append_diary_entry", entry_id: "route_a_diary_002" }
        ],
        next_events: ["route_a_room_signal_001"]
      },
      {
        event_id: "route_a_room_signal_001",
        route_id: "route_a",
        room_id: "signal",
        requirements: [
          { type: "route_status_equals", route_id: "route_a", value: "active" },
          { type: "event_completed", event_id: "route_a_room_observation_001" },
          { type: "event_enabled", event_id: "route_a_room_signal_001" },
          { type: "event_not_completed", event_id: "route_a_room_signal_001" }
        ],
        room_state_before: "normal",
        room_state_during: "observation_signal_received",
        room_state_after: "post_route_a",
        messages: ["観測中", "観測中のものを観測中", "管理人室"],
        interaction: { target: "signal-primary", action: "activate", repeatable: false },
        duration_ms: 7200,
        completion_requirements: [
          { type: "room_entered", room_id: "signal" },
          { type: "interaction_completed", target: "signal-primary" },
          { type: "sequence_finished", event_id: "route_a_room_signal_001" }
        ],
        effects: [
          { type: "complete_event", event_id: "route_a_room_signal_001" },
          { type: "set_room_state", room_id: "signal", value: "post_route_a" },
          { type: "enable_event", event_id: "route_a_manager_return_001" },
          { type: "set_target_room", room_id: "kanrinin" },
          { type: "append_diary_entry", entry_id: "route_a_diary_003" }
        ],
        next_events: ["route_a_manager_return_001"]
      },
      {
        event_id: "route_b_room_archive_001",
        route_id: "route_b",
        room_id: "archive",
        requirements: [
          { type: "route_status_equals", route_id: "route_b", value: "active" },
          { type: "event_completed", event_id: "route_b_phone_001" },
          { type: "event_enabled", event_id: "route_b_room_archive_001" },
          { type: "event_not_completed", event_id: "route_b_room_archive_001" }
        ],
        room_state_before: "normal",
        room_state_during: "unregistered_record_visible",
        room_state_after: "post_route_b",
        messages: [
          "記録番号：なし",
          "所有者：記録されていません",
          "状態：追加中",
          "管理人室へ入室",
          "赤い電話へ応答",
          "観測域へ入室",
          "受信域へ入室"
        ],
        interaction: { target: "archive-record", action: "open", repeatable: false },
        completion_requirements: [
          { type: "room_entered", room_id: "archive" },
          { type: "interaction_completed", target: "archive-record" },
          { type: "sequence_finished", event_id: "route_b_room_archive_001" }
        ],
        effects: [
          { type: "complete_event", event_id: "route_b_room_archive_001" },
          { type: "set_room_state", room_id: "archive", value: "post_route_b" },
          { type: "enable_event", event_id: "route_b_room_hyougi_001" },
          { type: "set_target_room", room_id: "hyougi" },
          { type: "append_diary_entry", entry_id: "route_b_diary_002" }
        ],
        next_events: ["route_b_room_hyougi_001"]
      },
      {
        event_id: "route_b_room_hyougi_001",
        route_id: "route_b",
        room_id: "hyougi",
        requirements: [
          { type: "route_status_equals", route_id: "route_b", value: "active" },
          { type: "event_completed", event_id: "route_b_room_archive_001" },
          { type: "event_enabled", event_id: "route_b_room_hyougi_001" },
          { type: "event_not_completed", event_id: "route_b_room_hyougi_001" }
        ],
        room_state_before: "normal",
        room_state_during: "unregistered_record_deliberation",
        room_state_after: "post_route_b",
        messages: [
          "議題：所有者を持たない記録の受け皿",
          "本人が存在しない以上、保存対象とは認められない。",
          "記録が継続している以上、本人の不存在は確定していない。",
          "記録から本人が発生した場合、誰が責任を持つのか。",
          "採決結果は保留。",
          "保管先のみ決定済み。"
        ],
        interaction: { target: "hyougi-record", action: "open", repeatable: false },
        completion_requirements: [
          { type: "room_entered", room_id: "hyougi" },
          { type: "interaction_completed", target: "hyougi-record" },
          { type: "sequence_finished", event_id: "route_b_room_hyougi_001" }
        ],
        effects: [
          { type: "complete_event", event_id: "route_b_room_hyougi_001" },
          { type: "set_room_state", room_id: "hyougi", value: "post_route_b" },
          { type: "enable_event", event_id: "route_b_room_gokuraku_001" },
          { type: "set_target_room", room_id: "gokuraku" },
          { type: "append_diary_entry", entry_id: "route_b_diary_003" }
        ],
        next_events: ["route_b_room_gokuraku_001"]
      },
      {
        event_id: "route_b_room_gokuraku_001",
        route_id: "route_b",
        room_id: "gokuraku",
        requirements: [
          { type: "route_status_equals", route_id: "route_b", value: "active" },
          { type: "event_completed", event_id: "route_b_room_hyougi_001" },
          { type: "event_enabled", event_id: "route_b_room_gokuraku_001" },
          { type: "event_not_completed", event_id: "route_b_room_gokuraku_001" }
        ],
        room_state_before: "normal",
        room_state_during: "unregistered_container_active",
        room_state_after: "post_route_b",
        messages: [
          "構成材料：不足",
          "所有者：未確定",
          "継続条件：観測",
          "停止していません"
        ],
        interaction: { target: "gokuraku-container", action: "open", repeatable: false },
        completion_requirements: [
          { type: "room_entered", room_id: "gokuraku" },
          { type: "interaction_completed", target: "gokuraku-container" },
          { type: "sequence_finished", event_id: "route_b_room_gokuraku_001" }
        ],
        effects: [
          { type: "complete_event", event_id: "route_b_room_gokuraku_001" },
          { type: "set_room_state", room_id: "gokuraku", value: "post_route_b" },
          { type: "enable_event", event_id: "route_b_manager_return_001" },
          { type: "set_target_room", room_id: "kanrinin" },
          { type: "append_diary_entry", entry_id: "route_b_diary_004" }
        ],
        next_events: ["route_b_manager_return_001"]
      },
      {
        event_id: "route_c_room_null_001",
        route_id: "route_c",
        room_id: "null",
        requirements: [
          { type: "route_status_equals", route_id: "route_c", value: "active" },
          { type: "event_completed", event_id: "route_c_phone_001" },
          { type: "event_enabled", event_id: "route_c_room_null_001" },
          { type: "event_not_completed", event_id: "route_c_room_null_001" }
        ],
        room_state_before: "normal",
        room_state_during: "persistent_fragment_visible",
        room_state_after: "post_route_c",
        messages: [
          "崩れていない",
          "崩れた場所に戻っている",
          "同じ形ではない"
        ],
        interaction: { target: "route-c-null-fragment", action: "touch", repeatable: false },
        completion_requirements: [
          { type: "room_entered", room_id: "null" },
          { type: "interaction_completed", target: "route-c-null-fragment" },
          { type: "sequence_finished", event_id: "route_c_room_null_001" }
        ],
        effects: [
          { type: "complete_event", event_id: "route_c_room_null_001" },
          { type: "set_room_state", room_id: "null", value: "post_route_c" },
          { type: "enable_event", event_id: "route_c_room_ma_001" },
          { type: "set_target_room", room_id: "ma" },
          { type: "append_diary_entry", entry_id: "route_c_diary_002" }
        ],
        next_events: ["route_c_room_ma_001"]
      },
      {
        event_id: "route_c_room_ma_001",
        route_id: "route_c",
        room_id: "ma",
        requirements: [
          { type: "route_status_equals", route_id: "route_c", value: "active" },
          { type: "event_completed", event_id: "route_c_room_null_001" },
          { type: "event_enabled", event_id: "route_c_room_ma_001" },
          { type: "event_not_completed", event_id: "route_c_room_ma_001" }
        ],
        room_state_before: "normal",
        room_state_during: "route_c_conversation",
        room_state_after: "post_route_c",
        messages: [
          "また来たか",
          "下で拾ったものの話だろう",
          "拾ってはいない？",
          "触ったなら同じだ",
          "壊れて戻るものは、戻っているんじゃない",
          "作り直されている",
          "作っている場所へ行け",
          "同じものだと思うなよ"
        ],
        interaction: { target: "route-c-ma-conversation", action: "listen", repeatable: false },
        completion_requirements: [
          { type: "room_entered", room_id: "ma" },
          { type: "interaction_completed", target: "route-c-ma-conversation" },
          { type: "sequence_finished", event_id: "route_c_room_ma_001" }
        ],
        effects: [
          { type: "complete_event", event_id: "route_c_room_ma_001" },
          { type: "set_room_state", room_id: "ma", value: "post_route_c" },
          { type: "enable_event", event_id: "route_c_room_particles_001" },
          { type: "set_target_room", room_id: "particles" },
          { type: "append_diary_entry", entry_id: "route_c_diary_003" }
        ],
        next_events: ["route_c_room_particles_001"]
      },
      {
        event_id: "route_c_room_particles_001",
        route_id: "route_c",
        room_id: "particles",
        requirements: [
          { type: "route_status_equals", route_id: "route_c", value: "active" },
          { type: "event_completed", event_id: "route_c_room_ma_001" },
          { type: "event_enabled", event_id: "route_c_room_particles_001" },
          { type: "event_not_completed", event_id: "route_c_room_particles_001" }
        ],
        room_state_before: "normal",
        room_state_during: "persistent_fragment_generation",
        room_state_after: "post_route_c",
        messages: [
          "構成中",
          "参照元：破損",
          "一致しません",
          "次を生成します"
        ],
        interaction: { target: "route-c-particles-generator", action: "activate", repeatable: false },
        completion_requirements: [
          { type: "room_entered", room_id: "particles" },
          { type: "interaction_completed", target: "route-c-particles-generator" },
          { type: "sequence_finished", event_id: "route_c_room_particles_001" }
        ],
        effects: [
          { type: "complete_event", event_id: "route_c_room_particles_001" },
          { type: "set_room_state", room_id: "particles", value: "post_route_c" },
          { type: "enable_event", event_id: "route_c_manager_return_001" },
          { type: "set_target_room", room_id: "kanrinin" },
          { type: "append_diary_entry", entry_id: "route_c_diary_004" }
        ],
        next_events: ["route_c_manager_return_001"]
      },
      {
        event_id: "route_d_room_ripple_001",
        route_id: "route_d",
        room_id: "ripple",
        requirements: [
          { type: "route_status_equals", route_id: "route_d", value: "active" },
          { type: "event_completed", event_id: "route_d_phone_001" },
          { type: "event_enabled", event_id: "route_d_room_ripple_001" },
          { type: "event_not_completed", event_id: "route_d_room_ripple_001" }
        ],
        room_state_before: "normal",
        room_state_during: "collective_reaction_ripple",
        room_state_after: "post_route_d",
        messages: ["一つではない", "同じ場所からでもない", "重なると、音に近づく"],
        interaction: { target: "route-d-ripple-center", action: "touch", repeatable: false },
        completion_requirements: [
          { type: "room_entered", room_id: "ripple" },
          { type: "interaction_completed", target: "route-d-ripple-center" },
          { type: "sequence_finished", event_id: "route_d_room_ripple_001" }
        ],
        effects: [
          { type: "complete_event", event_id: "route_d_room_ripple_001" },
          { type: "set_room_state", room_id: "ripple", value: "post_route_d" },
          { type: "enable_event", event_id: "route_d_room_colony_001" },
          { type: "set_target_room", room_id: "colony" },
          { type: "append_diary_entry", entry_id: "route_d_diary_002" }
        ],
        next_events: ["route_d_room_colony_001"]
      },
      {
        event_id: "route_d_room_colony_001",
        route_id: "route_d",
        room_id: "colony",
        requirements: [
          { type: "route_status_equals", route_id: "route_d", value: "active" },
          { type: "event_completed", event_id: "route_d_room_ripple_001" },
          { type: "event_enabled", event_id: "route_d_room_colony_001" },
          { type: "event_not_completed", event_id: "route_d_room_colony_001" }
        ],
        room_state_before: "normal",
        room_state_during: "shared_reaction_attempt",
        room_state_after: "post_route_d",
        messages: ["同期：不完全", "個体差：残存", "発声：未成立"],
        interaction: { target: "route-d-colony-core", action: "touch", repeatable: false },
        completion_requirements: [
          { type: "room_entered", room_id: "colony" },
          { type: "interaction_completed", target: "route-d-colony-core" },
          { type: "sequence_finished", event_id: "route_d_room_colony_001" }
        ],
        effects: [
          { type: "complete_event", event_id: "route_d_room_colony_001" },
          { type: "set_room_state", room_id: "colony", value: "post_route_d" },
          { type: "enable_event", event_id: "route_d_room_dot_art_001" },
          { type: "set_target_room", room_id: "dot-art" },
          { type: "append_diary_entry", entry_id: "route_d_diary_003" }
        ],
        next_events: ["route_d_room_dot_art_001"]
      },
      {
        event_id: "route_d_room_dot_art_001",
        route_id: "route_d",
        room_id: "dot-art",
        requirements: [
          { type: "route_status_equals", route_id: "route_d", value: "active" },
          { type: "event_completed", event_id: "route_d_room_colony_001" },
          { type: "event_enabled", event_id: "route_d_room_dot_art_001" },
          { type: "event_not_completed", event_id: "route_d_room_dot_art_001" }
        ],
        room_state_before: "normal",
        room_state_during: "low_resolution_reaction",
        room_state_after: "post_route_d",
        messages: ["読めません", "聞こえません", "でも、向きがあります"],
        interaction: { target: "route-d-dot-art-form", action: "touch", repeatable: false },
        completion_requirements: [
          { type: "room_entered", room_id: "dot-art" },
          { type: "interaction_completed", target: "route-d-dot-art-form" },
          { type: "sequence_finished", event_id: "route_d_room_dot_art_001" }
        ],
        effects: [
          { type: "complete_event", event_id: "route_d_room_dot_art_001" },
          { type: "set_room_state", room_id: "dot-art", value: "post_route_d" },
          { type: "enable_event", event_id: "route_d_room_matsuri_001" },
          { type: "set_target_room", room_id: "matsuri" },
          { type: "append_diary_entry", entry_id: "route_d_diary_004" }
        ],
        next_events: ["route_d_room_matsuri_001"]
      },
      {
        event_id: "route_d_room_matsuri_001",
        route_id: "route_d",
        room_id: "matsuri",
        requirements: [
          { type: "route_status_equals", route_id: "route_d", value: "active" },
          { type: "event_completed", event_id: "route_d_room_dot_art_001" },
          { type: "event_enabled", event_id: "route_d_room_matsuri_001" },
          { type: "event_not_completed", event_id: "route_d_room_matsuri_001" }
        ],
        room_state_before: "normal",
        room_state_during: "reaction_amplified_by_repetition",
        room_state_after: "post_route_d",
        messages: ["混ざっています", "揃っていません", "大きくなっています"],
        interaction: { target: "route-d-matsuri-repeat", action: "repeat", repeatable: false, required_count: 3 },
        completion_requirements: [
          { type: "room_entered", room_id: "matsuri" },
          { type: "interaction_completed", target: "route-d-matsuri-repeat" },
          { type: "sequence_finished", event_id: "route_d_room_matsuri_001" }
        ],
        effects: [
          { type: "complete_event", event_id: "route_d_room_matsuri_001" },
          { type: "set_room_state", room_id: "matsuri", value: "post_route_d" },
          { type: "enable_event", event_id: "route_d_room_namahage_001" },
          { type: "set_target_room", room_id: "namahage" },
          { type: "append_diary_entry", entry_id: "route_d_diary_005" }
        ],
        next_events: ["route_d_room_namahage_001"]
      },
      {
        event_id: "route_d_room_namahage_001",
        route_id: "route_d",
        room_id: "namahage",
        requirements: [
          { type: "route_status_equals", route_id: "route_d", value: "active" },
          { type: "event_completed", event_id: "route_d_room_matsuri_001" },
          { type: "event_enabled", event_id: "route_d_room_namahage_001" },
          { type: "event_not_completed", event_id: "route_d_room_namahage_001" }
        ],
        room_state_before: "normal",
        room_state_during: "almost_speaking",
        room_state_after: "post_route_d",
        messages: ["見ています", "開きかけています", "まだ、声ではありません", "戻ってください"],
        interaction: { target: "route-d-namahage-mouth", action: "hold", repeatable: false },
        completion_requirements: [
          { type: "room_entered", room_id: "namahage" },
          { type: "interaction_completed", target: "route-d-namahage-mouth" },
          { type: "sequence_finished", event_id: "route_d_room_namahage_001" }
        ],
        effects: [
          { type: "complete_event", event_id: "route_d_room_namahage_001" },
          { type: "set_room_state", room_id: "namahage", value: "post_route_d" },
          { type: "enable_event", event_id: "route_d_manager_return_001" },
          { type: "set_target_room", room_id: "kanrinin" },
          { type: "append_diary_entry", entry_id: "route_d_diary_006" }
        ],
        next_events: ["route_d_manager_return_001"]
      }
    ],
    managerEvents: [
      {
        event_id: "route_a_manager_return_001",
        route_id: "route_a",
        room_id: "kanrinin",
        requirements: [
          { type: "route_status_equals", route_id: "route_a", value: "active" },
          { type: "event_completed", event_id: "route_a_room_observation_001" },
          { type: "event_completed", event_id: "route_a_room_signal_001" },
          { type: "event_enabled", event_id: "route_a_manager_return_001" },
          { type: "event_not_completed", event_id: "route_a_manager_return_001" },
          { type: "room_entered_after_event", room_id: "kanrinin", after_event_id: "route_a_room_signal_001" }
        ],
        manager_state_sequence: ["hidden", "visible", "busy", "visible"],
        conversation: [
          { speaker: "manager", text: "電話、出たんですね。" },
          { speaker: "manager", text: "観測域から電話が来ることはありません。" },
          { speaker: "manager", text: "受信域が拾ったものを、電話が声にしたのかもしれません。" },
          { speaker: "manager", text: "でも、管理人室まで映っていたなら、こういうものも確認しておきましょう。" },
          { speaker: "manager", text: "上の階を一つ開けます。" },
          { speaker: "manager", text: "確認するかどうかは、次の電話が来てから決めてください。" }
        ],
        effects: [
          { type: "complete_event", event_id: "route_a_manager_return_001" },
          { type: "set_route_status", route_id: "route_a", value: "completed" },
          { type: "set_active_route", route_id: null },
          { type: "unlock_floor", floor_id: "floor_04" },
          { type: "increment_counter", counter_id: "completed_scenario_count", value: 1 },
          { type: "clear_target_room" },
          { type: "append_diary_entry", entry_id: "route_a_diary_complete" },
          { type: "enable_phone_pool", pool_id: "normal_route_phone_pool" },
          { type: "enable_event", event_id: "route_b_phone_001" },
          { type: "set_manager_state", state: "visible" }
        ],
        next_events: []
      },
      {
        event_id: "route_b_manager_return_001",
        route_id: "route_b",
        room_id: "kanrinin",
        requirements: [
          { type: "route_status_equals", route_id: "route_b", value: "active" },
          { type: "event_completed", event_id: "route_b_room_archive_001" },
          { type: "event_completed", event_id: "route_b_room_hyougi_001" },
          { type: "event_completed", event_id: "route_b_room_gokuraku_001" },
          { type: "event_enabled", event_id: "route_b_manager_return_001" },
          { type: "event_not_completed", event_id: "route_b_manager_return_001" },
          { type: "room_entered_after_event", room_id: "kanrinin", after_event_id: "route_b_room_gokuraku_001" }
        ],
        manager_state_sequence: ["away", "visible", "busy", "visible"],
        conversation: [
          { speaker: "manager", text: "見つかりました。" },
          { speaker: "manager", text: "本人がいない記録は、普通なら増えません。" },
          { speaker: "manager", text: "でも、あれは今も増えています。" },
          { speaker: "manager", text: "保存しているから増えるのか。" },
          { speaker: "manager", text: "増えているから保存されているのか。" },
          { speaker: "manager", text: "その判断は、まだ管理人の仕事ではありません。" },
          { speaker: "manager", text: "次の階を開けます。" },
          { speaker: "manager", text: "しばらく、あの記録には触れないでください。" }
        ],
        effects: [
          { type: "complete_event", event_id: "route_b_manager_return_001" },
          { type: "set_route_status", route_id: "route_b", value: "completed" },
          { type: "set_active_route", route_id: null },
          { type: "unlock_floor", floor_id: "floor_05" },
          { type: "increment_counter", counter_id: "completed_scenario_count", value: 1 },
          { type: "clear_target_room" },
          { type: "append_diary_entry", entry_id: "route_b_diary_complete" },
          { type: "enable_phone_pool", pool_id: "normal_route_phone_pool" },
          { type: "enable_event", event_id: "route_c_phone_001" },
          { type: "set_manager_state", state: "visible" }
        ],
        next_events: []
      },
      {
        event_id: "route_c_manager_return_001",
        route_id: "route_c",
        room_id: "kanrinin",
        requirements: [
          { type: "route_status_equals", route_id: "route_c", value: "active" },
          { type: "event_completed", event_id: "route_c_room_null_001" },
          { type: "event_completed", event_id: "route_c_room_ma_001" },
          { type: "event_completed", event_id: "route_c_room_particles_001" },
          { type: "event_enabled", event_id: "route_c_manager_return_001" },
          { type: "event_not_completed", event_id: "route_c_manager_return_001" },
          { type: "room_entered_after_event", room_id: "kanrinin", after_event_id: "route_c_room_particles_001" }
        ],
        manager_state_sequence: ["visible", "visible", "busy", "visible"],
        conversation: [
          { speaker: "manager", text: "同じものはありましたか" },
          { speaker: "manager", text: "なかったんですね" },
          { speaker: "manager", text: "なら、あれは直っているんじゃありません" },
          { speaker: "manager", text: "壊れるたびに、似たものが置き直されています" },
          { speaker: "manager", text: "前のものがどこへ行くのかは分かりません" },
          { speaker: "manager", text: "次の階を開けます" },
          { speaker: "manager", text: "上に行けば、もっと完成したものがあるとは限りません" },
          { speaker: "manager", text: "むしろ逆かもしれません" }
        ],
        effects: [
          { type: "complete_event", event_id: "route_c_manager_return_001" },
          { type: "set_route_status", route_id: "route_c", value: "completed" },
          { type: "set_active_route", route_id: null },
          { type: "unlock_floor", floor_id: "floor_06" },
          { type: "increment_counter", counter_id: "completed_scenario_count", value: 1 },
          { type: "clear_target_room" },
          { type: "append_diary_entry", entry_id: "route_c_diary_complete" },
          { type: "enable_phone_pool", pool_id: "normal_route_phone_pool" },
          { type: "enable_event", event_id: "route_d_phone_001" },
          { type: "set_manager_state", state: "visible" }
        ],
        next_events: []
      },
      {
        event_id: "route_d_manager_return_001",
        route_id: "route_d",
        room_id: "kanrinin",
        requirements: [
          { type: "route_status_equals", route_id: "route_d", value: "active" },
          { type: "event_completed", event_id: "route_d_room_ripple_001" },
          { type: "event_completed", event_id: "route_d_room_colony_001" },
          { type: "event_completed", event_id: "route_d_room_dot_art_001" },
          { type: "event_completed", event_id: "route_d_room_matsuri_001" },
          { type: "event_completed", event_id: "route_d_room_namahage_001" },
          { type: "event_enabled", event_id: "route_d_manager_return_001" },
          { type: "event_not_completed", event_id: "route_d_manager_return_001" },
          { type: "room_entered_after_event", room_id: "kanrinin", after_event_id: "route_d_room_namahage_001" }
        ],
        manager_state_sequence: ["visible", "visible", "busy", "visible"],
        conversation: [
          { speaker: "manager", text: "聞こえましたか" },
          { speaker: "manager", text: "聞こえなかったなら、それで合っています" },
          { speaker: "manager", text: "あれはまだ声ではありません" },
          { speaker: "manager", text: "部屋ごとに残っていた反応を、無理に集めただけです" },
          { speaker: "manager", text: "一つに見えても、一人とは限りません" },
          { speaker: "manager", text: "一人に見えなくても、呼んでいるとは限りません" },
          { speaker: "manager", text: "ここから先は、開けるだけでは進めません" },
          { speaker: "manager", text: "触ったものが、次の形になります" }
        ],
        effects: [
          { type: "complete_event", event_id: "route_d_manager_return_001" },
          { type: "set_route_status", route_id: "route_d", value: "completed" },
          { type: "set_active_route", route_id: null },
          { type: "increment_counter", counter_id: "completed_scenario_count", value: 1 },
          { type: "clear_target_room" },
          { type: "append_diary_entry", entry_id: "route_d_diary_complete" },
          { type: "enable_phone_pool", pool_id: "normal_route_phone_pool" },
          { type: "set_route_status", route_id: "route_e", value: "available" },
          { type: "set_state_value", key: "final_route_available", value: true },
          { type: "set_state_value", key: "route_e_stage", value: "route_e_available" },
          { type: "set_state_value", key: "top_floor_unlocked", value: false },
          { type: "set_state_value", key: "top_floor_keyhole_active", value: false },
          { type: "enable_event", event_id: "route_e_phone_001" },
          { type: "set_manager_state", state: "visible" }
        ],
        next_events: []
      }
    ],
    diaryEntries: [
      {
        entry_id: "route_a_diary_001",
        route_id: "route_a",
        title: "混線している観測 1",
        text: "観測対象から通常経路ではない受信あり。発信元を観測域として記録する。回線経路は確認できず。"
      },
      {
        entry_id: "route_a_diary_002",
        route_id: "route_a",
        title: "混線している観測 2",
        text: "観測対象に別系統の映像が混入。受信機能を持つ部屋の確認が必要。"
      },
      {
        entry_id: "route_a_diary_003",
        route_id: "route_a",
        title: "混線している観測 3",
        text: "受信域で観測域の映像を確認。画面内に管理人室を示す断片あり。現象は停止していない。"
      },
      {
        entry_id: "route_a_diary_complete",
        route_id: "route_a",
        title: "混線している観測 完了",
        text: "観測域および受信域を確認。発信元は特定できず。上階の開錠を一部解除。"
      },
      {
        entry_id: "route_b_diary_001",
        route_id: "route_b",
        title: "記録されていない人 1",
        text: "住人台帳に存在しない発信者から受信。氏名欄、部屋欄、登録番号欄なし。残留域の記録を確認する。"
      },
      {
        entry_id: "route_b_diary_002",
        route_id: "route_b",
        title: "記録されていない人 2",
        text: "所有者不在の記録を確認。記録内容は現在も追加されている。保管判断に関する評議記録を確認する。"
      },
      {
        entry_id: "route_b_diary_003",
        route_id: "route_b",
        title: "記録されていない人 3",
        text: "所有者不在の記録に関する評議を確認。破棄、保存ともに採決されていない。記録本体の別室移送を確認する。"
      },
      {
        entry_id: "route_b_diary_004",
        route_id: "route_b",
        title: "記録されていない人 4",
        text: "所有者不在の記録の保管先を確認。保管物は完成していない。記録処理は現在も継続中。"
      },
      {
        entry_id: "route_b_diary_complete",
        route_id: "route_b",
        title: "記録されていない人 完了",
        text: "所有者不在の記録の保管状態を確認。記録は停止していない。判断は保留。次階の開錠を解除。"
      },
      {
        entry_id: "route_c_diary_001",
        route_id: "route_c",
        title: "Route_C 1",
        text: "Unidentified call received. Most of the sound was damaged. Periodic contact noise was detected inside the collapse sound. Check the collapse area."
      },
      {
        entry_id: "route_c_diary_002",
        route_id: "route_c",
        title: "Route_C 2",
        text: "A persistent object was found inside the collapse area. Each reconstruction changes its details. Ask the resident in Ma."
      },
      {
        entry_id: "route_c_diary_003",
        route_id: "route_c",
        title: "Route_C 3",
        text: "The object may not be restored. It may be generated again each time. Check the likely generation room."
      },
      {
        entry_id: "route_c_diary_004",
        route_id: "route_c",
        title: "Route_C 4",
        text: "A similar form appeared in the particle structure. It does not match the collapse object. The order of collapse and generation is unknown."
      },
      {
        entry_id: "route_c_diary_complete",
        route_id: "route_c",
        title: "Route_C complete",
        text: "Collapse area and particle structure checked. The object is likely repeated generation, not restoration. Source and disposal remain unknown. Next floor unlocked."
      },
      {
        entry_id: "route_d_diary_001",
        route_id: "route_d",
        title: "Route_D 1",
        text: "複数の発信元を含む着信あり。音声は単一の声として成立していない。波形に伝播反応を確認。波紋を確認する。"
      },
      {
        entry_id: "route_d_diary_002",
        route_id: "route_d",
        title: "Route_D 2",
        text: "波紋内に複数の発生点を確認。波形は単一の震源を持たない。反応は群体領域へ伝播。"
      },
      {
        entry_id: "route_d_diary_003",
        route_id: "route_d",
        title: "Route_D 3",
        text: "群体領域で同期反応を確認。完全な統一には至らず。反応は低解像度の形へ移行。"
      },
      {
        entry_id: "route_d_diary_004",
        route_id: "route_d",
        title: "Route_D 4",
        text: "低解像度の発声形状を確認。文字、顔、音声波形のいずれにも確定せず。反応は反復操作により増幅可能。"
      },
      {
        entry_id: "route_d_diary_005",
        route_id: "route_d",
        title: "Route_D 5",
        text: "祭事操作により反応が増幅。掛け声に電話音声と一致する断片を確認。反応は発声器官を持つ対象へ移動。"
      },
      {
        entry_id: "route_d_diary_006",
        route_id: "route_d",
        title: "Route_D 6",
        text: "なまはげ面に発声直前の反応を確認。口元は開いたが、音声として成立せず。反応の集合は未完了のまま停止。管理人室へ戻る。"
      },
      {
        entry_id: "route_d_diary_complete",
        route_id: "route_d",
        title: "Route_D complete",
        text: "6F各領域で集合反応を確認。波形、群体、低解像度形状、祭事音、面反応は同一現象の断片である可能性あり。音声としては未成立。今後の進行には、開放ではなく接触条件が必要となる。"
      }
    ],
    branchSlots: [
      { branch_id: "route_a_phone_ignored", enabled: false, attach_after_event: "route_a_phone_001" },
      { branch_id: "route_a_observation_repeat", enabled: false, attach_after_event: "route_a_room_observation_001" },
      { branch_id: "route_a_signal_alternate", enabled: false, attach_after_event: "route_a_room_signal_001" },
      { branch_id: "route_a_manager_absent", enabled: false, attach_after_event: "route_a_manager_return_001" },
      { branch_id: "route_b_unregistered_repeat", enabled: false, attach_after_event: "route_b_room_archive_001" },
      { branch_id: "route_c_fragment_repeat", enabled: false, attach_after_event: "route_c_room_null_001" },
      { branch_id: "route_d_collective_repeat", enabled: false, attach_after_event: "route_d_room_ripple_001" }
    ]
  };
})();
