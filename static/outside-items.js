(function () {
  const iconBase = "/static/outside/icons/";

  window.KYOUKAI_OUTSIDE_AMAZON_LINKS = [
    "https://amzn.to/4urrBMw",
    "https://amzn.to/4wUrif2",
    "https://amzn.to/4dxEJKg",
    "https://amzn.to/4v0SZAM",
    "https://amzn.to/3RtEN4Z",
    "https://amzn.to/3RtEN4Z",
    "https://amzn.to/4x4ZG70",
    "https://amzn.to/4wUrw5S",
    "https://amzn.to/4usXoN5",
    "https://amzn.to/4wQUJhN",
    "https://amzn.to/4dJdrzj",
    "https://amzn.to/4fqmasP",
    "https://amzn.to/4v1yC6K"
  ];

  function randomAmazonItem(slot, label, shortLabel, body, icon) {
    return {
      slot,
      label,
      shortLabel,
      body,
      icon: iconBase + icon,
      randomAmazon: true,
      disclosure: "PR / Amazon Associate random link"
    };
  }

  window.KYOUKAI_OUTSIDE_ITEMS = {
    "item-01": randomAmazonItem(
      1,
      "ALTAR ARTIFACT",
      "ALTAR",
      "An external object left near the entrance.",
      "item_01.png"
    ),
    "item-02": randomAmazonItem(
      2,
      "FOUND OBJECT 02",
      "OBJ 02",
      "A second object recovered from outside.",
      "item_02.png"
    ),
    "item-03": randomAmazonItem(
      3,
      "FOUND OBJECT 03",
      "OBJ 03",
      "A third object recovered from outside.",
      "item_03.png"
    ),
    "item-04": {
      slot: 4,
      label: "BOUNDARY BOX",
      shortLabel: "BOX",
      body: "A small box used for boundary maintenance.",
      icon: iconBase + "item_04.png",
      href: "https://ofuse.me/be78f6ed",
      target: "_blank",
      rel: "noopener noreferrer",
      disclosure: "External offering box"
    },
    "item-05": randomAmazonItem(
      5,
      "FOUND OBJECT 05",
      "OBJ 05",
      "Unassigned external object.",
      "item_05.png"
    ),
    "item-06": randomAmazonItem(
      6,
      "FOUND OBJECT 06",
      "OBJ 06",
      "Unassigned external object.",
      "item_06.png"
    ),
    "item-07": randomAmazonItem(
      7,
      "FOUND OBJECT 07",
      "OBJ 07",
      "Unassigned external object.",
      "item_07.png"
    ),
    "item-08": randomAmazonItem(
      8,
      "FOUND OBJECT 08",
      "OBJ 08",
      "Unassigned external object.",
      "item_08.png"
    ),
    "item-09": randomAmazonItem(
      9,
      "FOUND OBJECT 09",
      "OBJ 09",
      "Unassigned external object.",
      "item_09.png"
    ),
    "item-10": randomAmazonItem(
      10,
      "FOUND OBJECT 10",
      "OBJ 10",
      "Unassigned external object.",
      "item_10.png"
    ),
    "item-11": randomAmazonItem(
      11,
      "FOUND OBJECT 11",
      "OBJ 11",
      "Unassigned external object.",
      "item_11.png"
    ),
    "item-12": randomAmazonItem(
      12,
      "FOUND OBJECT 12",
      "OBJ 12",
      "Unassigned external object.",
      "item_12.png"
    ),
    "item-13": randomAmazonItem(
      13,
      "FOUND OBJECT 13",
      "OBJ 13",
      "Unassigned external object.",
      "item_13.png"
    ),
    "item-14": randomAmazonItem(
      14,
      "FOUND OBJECT 14",
      "OBJ 14",
      "Unassigned external object.",
      "item_14.png"
    ),
    "item-15": randomAmazonItem(
      15,
      "FOUND OBJECT 15",
      "OBJ 15",
      "Unassigned external object.",
      "item_15.png"
    ),
    "item-16": {
      slot: 16,
      label: "RETURN LINE",
      shortLabel: "000",
      body: "Return to the first boundary.",
      icon: iconBase + "item_16.png",
      href: "/"
    }
  };

  window.KYOUKAI_OUTSIDE_GRID = [
    "item-01",
    "item-02",
    "item-03",
    "item-04",
    "item-05",
    "item-06",
    "item-07",
    "item-08",
    "item-09",
    "item-10",
    "item-11",
    "item-12",
    "item-13",
    "item-14",
    "item-15",
    "item-16"
  ];
})();
