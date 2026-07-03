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

  window.KYOUKAI_SCENARIO_EVENTS = {
    version: "route-b-v1",
    routes: [routeA, routeB],
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
          { type: "event_not_completed", event_id: "route_b_phone_001" },
          { type: "room_entered_after_event", room_id: "kanrinin", after_event_id: "route_a_manager_return_001" }
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
      }
    ],
    roomEvents: [
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
      }
    ],
    branchSlots: [
      { branch_id: "route_a_phone_ignored", enabled: false, attach_after_event: "route_a_phone_001" },
      { branch_id: "route_a_observation_repeat", enabled: false, attach_after_event: "route_a_room_observation_001" },
      { branch_id: "route_a_signal_alternate", enabled: false, attach_after_event: "route_a_room_signal_001" },
      { branch_id: "route_a_manager_absent", enabled: false, attach_after_event: "route_a_manager_return_001" },
      { branch_id: "route_b_unregistered_repeat", enabled: false, attach_after_event: "route_b_room_archive_001" }
    ]
  };
})();
