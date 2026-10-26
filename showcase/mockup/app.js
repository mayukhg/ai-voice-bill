(function () {
  const bills = [
    {
      id: "BILL-001",
      type: "utility",
      label: "Electricity",
      amount: 150.0,
      due: "in 5 days",
      urgent: true,
      paid: false,
    },
    {
      id: "BILL-003",
      type: "subscription",
      label: "Streaming",
      amount: 29.99,
      due: "in 3 days",
      urgent: true,
      paid: false,
    },
    {
      id: "BILL-002",
      type: "credit_card",
      label: "Credit card",
      amount: 500.0,
      due: "in 10 days",
      urgent: false,
      paid: false,
    },
  ];

  const screens = {
    landing: document.getElementById("screen-landing"),
    bills: document.getElementById("screen-bills"),
    voice: document.getElementById("screen-voice"),
    otp: document.getElementById("screen-otp"),
    done: document.getElementById("screen-done"),
  };

  const transcript = document.getElementById("transcript");
  const deviceUtterance = document.getElementById("device-utterance");
  const deviceGlow = document.getElementById("device-glow");
  const livePill = document.getElementById("live-pill");
  const billList = document.getElementById("bill-list");
  const billsSummary = document.getElementById("bills-summary");

  function money(n) {
    return n.toLocaleString("en-US", { style: "currency", currency: "USD" });
  }

  function show(name) {
    Object.entries(screens).forEach(([key, el]) => {
      const on = key === name;
      el.hidden = !on;
      el.classList.toggle("is-active", on);
    });
    window.scrollTo(0, 0);
    if (name === "bills") renderBills();
    if (name === "voice" && !transcript.children.length) {
      deviceUtterance.textContent = "“Alexa, ask VoiceBill what’s due.”";
    }
  }

  function renderBills() {
    billList.innerHTML = "";
    const unpaid = bills.filter((b) => !b.paid);
    bills.forEach((b) => {
      const li = document.createElement("li");
      li.className = "bill-row" + (b.paid ? " is-paid" : "");
      li.innerHTML =
        '<span class="bill-type">' +
        b.label +
        '</span><span class="bill-amount' +
        (b.urgent && !b.paid ? " urgent" : "") +
        '">' +
        money(b.amount) +
        (b.paid ? " · paid" : "") +
        '</span><span class="bill-due">' +
        (b.paid ? "Settled today" : "Due " + b.due + " · " + b.id) +
        "</span>";
      billList.appendChild(li);
    });
    const total = unpaid.reduce((s, b) => s + b.amount, 0);
    billsSummary.textContent =
      unpaid.length + " unpaid · " + money(total) + " outstanding";
  }

  function sleep(ms) {
    return new Promise((r) => setTimeout(r, ms));
  }

  function addBubble(who, text) {
    const div = document.createElement("div");
    div.className = "bubble " + who;
    div.textContent = text;
    transcript.appendChild(div);
    div.scrollIntoView({ behavior: "smooth", block: "nearest" });
  }

  function setSpeaking(on, label) {
    deviceGlow.classList.toggle("active", on);
    livePill.textContent = label || (on ? "Speaking" : "Listening");
    livePill.classList.toggle("speak", on && label !== "Listening");
  }

  async function runReminders() {
    show("voice");
    transcript.innerHTML = "";
    setSpeaking(false, "Listening");
    deviceUtterance.textContent = "“Alexa, ask VoiceBill what’s due.”";
    await sleep(400);
    addBubble("user", "Alexa, ask VoiceBill what’s due.");
    await sleep(700);
    setSpeaking(true, "Speaking");
    const unpaid = bills.filter((b) => !b.paid);
    const first = unpaid[0];
    const msg = first
      ? "You have " +
        unpaid.length +
        " bills due. Your " +
        first.label.toLowerCase() +
        " bill of " +
        money(first.amount) +
        " is due " +
        first.due +
        ". Would you like to pay it now?"
      : "You have no bills due at this time.";
    deviceUtterance.textContent = "“" + msg + "”";
    addBubble("alexa", msg);
    await sleep(1200);
    setSpeaking(false, "Listening");
  }

  async function runPay() {
    show("voice");
    const util = bills.find((b) => b.id === "BILL-001");
    if (!util || util.paid) {
      transcript.innerHTML = "";
      addBubble("alexa", "That electricity bill is already paid. Nice work.");
      return;
    }
    transcript.innerHTML = "";
    setSpeaking(false, "Listening");
    deviceUtterance.textContent = "“I want to pay my electricity bill.”";
    await sleep(350);
    addBubble("user", "I want to pay my electricity bill.");
    await sleep(650);
    setSpeaking(true, "Speaking");
    const msg =
      "Paying electricity for " +
      money(150) +
      ". An OTP has been sent to your registered mobile. Please provide the code.";
    deviceUtterance.textContent = "“" + msg + "”";
    addBubble("alexa", msg);
    await sleep(1100);
    setSpeaking(false, "Listening");
    show("otp");
  }

  function verifyPay() {
    const util = bills.find((b) => b.id === "BILL-001");
    if (util) util.paid = true;
    show("done");
  }

  function resetDemo() {
    bills.forEach((b) => {
      b.paid = false;
    });
    transcript.innerHTML = "";
    show("landing");
  }

  document.querySelectorAll("[data-go]").forEach((el) => {
    el.addEventListener("click", () => {
      const target = el.getAttribute("data-go");
      if (el.getAttribute("data-flow") === "remind") {
        runReminders();
        return;
      }
      show(target);
    });
  });

  document.getElementById("btn-remind").addEventListener("click", runReminders);
  document.getElementById("btn-pay").addEventListener("click", runPay);
  document.getElementById("btn-verify").addEventListener("click", verifyPay);
  document.getElementById("btn-reset").addEventListener("click", resetDemo);

  // Deep-link support for screenshots / walkthrough: ?screen=bills
  const params = new URLSearchParams(window.location.search);
  const initial = params.get("screen");
  if (initial && screens[initial]) {
    show(initial);
    if (initial === "voice" && params.get("flow") === "remind") runReminders();
    if (initial === "voice" && params.get("flow") === "pay") runPay();
  } else {
    show("landing");
  }

  window.VoiceBillMock = { show, runReminders, runPay, verifyPay, resetDemo, bills };
})();
