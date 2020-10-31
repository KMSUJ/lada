let switchWolny = document.querySelector("#free");
let switchKomisja = document.querySelector("#covision");
let switchesBoard = document.querySelectorAll("input.switch:not(#free)")

for (s of switchesBoard) {
  s.addEventListener("click", toggleBoard);
  if (s.checked) {
    selectWolny()
  }
}

switchWolny.addEventListener("click", toggleWolny);

function toggleBoard() {
  checkedCount = countSwitches();
  if (this.checked == true) {
    if (this != switchKomisja) selectWolny();
    if (checkedCount > 2) {
      disableSwitches();
    }
  } else if (checkedCount > 0) {
    enableSwitches();
  }
}

function toggleWolny() {
  checkedCount = countSwitches();
  if (this.checked != true) deselectBoard();
  if (checkedCount > 0) enableSwitches();
}

function deselectBoard() {
  for (s of switchesBoard) {
    if (s != switchKomisja) s.checked = false;
  }
}

function selectWolny() {
  switchWolny.checked = true;
}

function deselectWolny() {
  switchWolny.checked = false;
}

function countSwitches() {
  c = 0;
  for (s of switchesBoard) {
    if (s.checked == true) {
      c = c+1;
    }
  }
  return c;
}

function disableSwitches() {
  for (s of switchesBoard) {
    if (s.checked == false) {
      s.disabled = true;
    }
  }
}

function enableSwitches() {
  for (s of switchesBoard) {
    s.disabled = false;
  }
}
