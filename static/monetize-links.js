(function () {
  window.KYOUKAI_MONETIZE_LINKS = {
    outside: {
      enabled: true,
      href: "/outside",
      label: "外部接続",
      sublabel: "OUTSIDE"
    },
    sections: [
      {
        id: "carry",
        title: "持ち帰り品",
        note: "この場所に残っていた外部接続物。",
        items: [
          {
            label: "漂着物 / ALTAR",
            body: "入口付近で検出された外部物品。",
            href: "https://amzn.to/4nIXnSI",
            rel: "sponsored noopener noreferrer",
            target: "_blank",
            disclosure: "PR / Amazonアソシエイトリンクを含みます"
          }
        ]
      },
      {
        id: "route",
        title: "回遊端子",
        note: "別域へ戻るための短い接続。",
        items: [
          { label: "入口", body: "漂流を再開する。", href: "/" },
          { label: "観測室", body: "観測を再接続する。", href: "/observation" },
          { label: "信号室", body: "映像信号へ戻る。", href: "/signal" },
          { label: "記録室", body: "残された像を確認する。", href: "/archive" }
        ]
      },
      {
        id: "qr",
        title: "SHORTS接続口",
        note: "YouTube Shortsや外部SNSからの流入先。",
        items: [
          {
            label: "共通着地点",
            body: "QRや説明欄にはこのページを使う。",
            href: "/outside?utm_source=youtube&utm_medium=shorts&utm_campaign=outside_core"
          }
        ]
      }
    ]
  };
})();
