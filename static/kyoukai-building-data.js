(function () {
  "use strict";

  window.KYOUKAI_BUILDING = {
    version: "scenario-mode-v1",
    roomsPerFloor: 5,
    initialScenarioFloors: 3,
    floorStates: {
      unlockedUntil: 3,
      upperDefault: "story_only"
    },
    topFloorRoom: {
      id: "top-floor",
      name: "top-floor",
      label: "KEY",
      href: "/top-floor",
      image: "/static/images/entrances/entrance-top-floor.png",
      roomImage: "/static/images/top-floor/top-floor-room.png",
      material: "shrine",
      residentId: "top_floor",
      defaultState: "locked",
      topFloorOnly: true
    },
    routes: [
      {
        id: "route_a",
        name: "Route_A",
        startRequirements: [{ type: "mode", value: "scenario" }],
        completionRequirements: [],
        failureRequirements: [],
        branches: []
      }
    ],
    rooms: [
      { roomIndex: 0, id: "kanrinin", name: "kanrinin", label: "MGR", href: "/kanrinin", image: "/static/images/entrances/entrance-kanrinin.png", material: "door", residentId: "kanrinin", defaultState: "normal" },

      { roomIndex: 5, id: "observation", name: "observation", label: "OBS", href: "/observation", image: "/static/images/entrances/entrance-observation.png", material: "mirror", residentId: "observer", defaultState: "normal" },
      { roomIndex: 6, id: "observer", name: "observer", label: "OBR", href: "/observer", image: "/static/images/entrances/entrance-observer.png", material: "shrine", residentId: "observer", defaultState: "normal" },
      { roomIndex: 7, id: "archive", name: "archive", label: "ARC", href: "/archive", image: "/static/images/entrances/entrance-archive.png", material: "box", residentId: "archivist", defaultState: "normal" },

      { roomIndex: 10, id: "signal", name: "signal", label: "SIG", href: "/signal", image: "/static/images/entrances/entrance-signal.png", material: "speaker", residentId: "signal", defaultState: "normal" },
      { roomIndex: 11, id: "news", name: "news", label: "NEWS", href: "/typhoon-news/", image: "/static/images/entrances/news.png", material: "door", residentId: "news", defaultState: "normal" },
      { roomIndex: 12, id: "daimyojin", name: "daimyojin", label: "DMJ", href: "/daimyojin", image: "/static/images/entrances/entrance-daimyojin.png", material: "shrine", residentId: "daimyojin", defaultState: "normal" },

      { roomIndex: 15, id: "hyougi", name: "hyougi", label: "HYO", href: "/hyougi", image: "/static/images/entrances/entrance-hyougi.png", material: "paper", residentId: "hyougi", defaultState: "locked" },
      { roomIndex: 16, id: "gokuraku", name: "gokuraku", label: "GOK", href: "/gokuraku", image: "/static/images/entrances/entrance-gokuraku.png", material: "shrine", residentId: "gokuraku", defaultState: "locked" },
      { roomIndex: 17, id: "exit", name: "exit", label: "EXT", href: "/exit", image: "/static/images/entrances/entrance-exit.png", material: "door", residentId: "exit", defaultState: "locked" },

      { roomIndex: 20, id: "null", name: "null", label: "NUL", href: "/null", image: "/static/images/entrances/entrance-null.png", material: "crack", residentId: "null", defaultState: "locked" },
      { roomIndex: 21, id: "ma", name: "ma", label: "MA", href: "/ma", image: "/static/images/entrances/entrance-ma.png", material: "mirror", residentId: "ma", defaultState: "locked" },
      { roomIndex: 22, id: "particles", name: "particles", label: "PRT", href: "/particles", image: "/static/images/entrances/entrance-particles.png?v=20260625c", material: "mirror", residentId: "particles", defaultState: "locked" },

      { roomIndex: 25, id: "ripple", name: "ripple", label: "RPL", href: "/ripple", image: "/static/images/entrances/entrance-ripple.png?v=20260625b", material: "crack", residentId: "ripple", defaultState: "locked" },
      { roomIndex: 26, id: "colony", name: "COLONY", label: "COL", href: "/colony", image: "/static/images/colony/entrance-colony.png", material: "crack", residentId: "colony", defaultState: "locked" },
      { roomIndex: 27, id: "dot-art", name: "dot-art", label: "DOT", href: "/dot-art", image: "/static/entrance-dot-art.png", material: "crack", residentId: "dot_art", defaultState: "locked" },
      { roomIndex: 28, id: "matsuri", name: "matsuri", label: "MAT", href: "/matsuri", image: "/static/images/entrances/entrance-matsuri.png", material: "shrine", residentId: "matsuri", defaultState: "locked" },
      { roomIndex: 29, id: "namahage", name: "namahage", label: "NMH", href: "/namahage", image: "/static/images/entrances/entrance-namahage.png", material: "crack", residentId: "namahage", defaultState: "locked" }
    ],
    residents: [
      { id: "kanrinin", state: "hidden", roomId: "kanrinin" },
      { id: "observer", state: "hidden", roomId: "observation" },
      { id: "archivist", state: "hidden", roomId: "archive" },
      { id: "signal", state: "hidden", roomId: "signal" },
      { id: "top_floor", state: "hidden", roomId: "top-floor" }
    ]
  };
})();
