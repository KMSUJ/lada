window.onload = positionImages;
window.addEventListener('resize', positionImages);

function positionImages() {
  document.querySelector("#historyimg").style.top = scrollheight(document.querySelector("#kmsintro"));
  document.querySelector("#cnfrncimg").style.top = scrollheight(document.querySelector("#history"));
  document.querySelector("#backsideimg").style.top = scrollheight(document.querySelector("#cnfrnc"));
}

function scrollheight(article) {
  return `${(article.clientHeight + article.offsetTop)*8/9}px`
}
