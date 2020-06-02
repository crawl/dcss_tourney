// Set relative times
window.addEventListener("load", function() {
  const els = document.getElementsByClassName('moment-js-relative-time');
  for (const el of els) {
    const data_timestamp = el.attributes["data-timestamp"].value;
    const timestamp = moment.utc(data_timestamp, moment.ISO_8601, true);
    if (!timestamp.isValid()) {
      this.console.log(`Invalid timestamp: ${data_timestamp}`);
      continue;
    }
    const whenString = timestamp.fromNow();
    el.innerHTML = `(${whenString})`;
  }
});
