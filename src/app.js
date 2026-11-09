const $ = (id) => document.getElementById(id);

function showMessage(kind, text) {
  const box = $("message");
  box.className = kind;
  box.textContent = text;          // text, never HTML (design doc 7.4)
  box.hidden = false;
}

function clearAll() {
  $("message").hidden = true;
  $("asm").replaceChildren();
  $("mc").replaceChildren();
}

function addRow(parent, text) {
  const div = document.createElement("div");
  div.className = "row";
  div.textContent = text;
  parent.appendChild(div);
}

const hex = (n) => "0x" + n.toString(16);

async function compile() {
  clearAll();
  let res, data;
  try {
    res = await fetch("/api/compile", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ source: $("source").value, optimization: $("opt").value }),
    });
    data = await res.json();
  } catch (e) {
    showMessage("error", "Could not reach the server.");
    return;
  }

  if (!res.ok) {                                   // request or server error
    showMessage("error", "Request error: " + (data.message || res.status));
    return;
  }
  if (!data.success) {                             // C code did not compile
    showMessage("error", "Compilation failed:\n" + data.diagnostics.join("\n"));
    return;
  }

  for (const a of data.assembly) {
    addRow($("asm"), `${hex(a.address)}  ${a.text}   [line ${a.source_line ?? "none"}]`);
  }
  for (const i of data.instructions) {
    const label = i.decode_status === "supported"
      ? `${i.mnemonic} (${i.format}-type)`
      : `${i.decode_status} instruction`;
    addRow($("mc"), `${hex(i.address)}  ${i.hex}\n${i.binary}\n${label}\n`);
  }
}

$("compile").addEventListener("click", compile);