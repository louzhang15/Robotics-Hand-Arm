// Runs actual C++ executor logic compiled to WebAssembly, not a Python mirror.
const fs = require('node:fs');
const assert = require('node:assert/strict');
const near = (actual, expected) => assert.ok(Math.abs(actual - expected) < 1e-5,
  `${actual} differs from ${expected}`);

(async () => {
  const { instance } = await WebAssembly.instantiate(fs.readFileSync(process.argv[2]));
  const s = instance.exports;
  s.reset();
  assert.equal(s.relaxed(), 1);
  near(s.current(6), 0.5);
  assert.equal(s.command(1, 6, 100), 0);
  assert.equal(s.relaxed(), 1);
  assert.equal(s.lastCommand(), 0);
  assert.equal(s.badCommand(200), 0);
  near(s.target(0), 0); // no partial target mutation
  assert.equal(s.command(2, 7, 100), 1);
  near(s.target(0), 1); // finite out-of-range targets clamp
  assert.equal(s.cal(0, 120, 60), 0); // active calibration rejected
  s.tick(120);
  near(s.current(0), 0.04);
  near(s.current(6), 0.54);
  assert.equal(s.badCommand(599), 0);
  s.tick(600); // malformed command did not refresh 500 ms watchdog
  assert.equal(s.watchdog(), 1);
  near(s.target(0), 0);
  near(s.target(6), 0.5);
  near(s.current(0), 0);
  s.relax();
  assert.equal(s.cal(-1, 60, 120), 0);
  assert.equal(s.cal(7, 60, 120), 0);
  assert.equal(s.cal(0, 90, 90), 0);
  assert.equal(s.cal(0, -1, 120), 0);
  assert.equal(s.cal(0, 60, Infinity), 0);
  assert.equal(s.cal(0, 120, 60), 1); // mirrored mounting supported
  s.command(1, 7, 1000);
  s.tick(1020);
  near(s.angle(0), 117.6);
  s.relax();
  const held = s.current(0);
  s.tick(5000);
  near(s.current(0), held); // relaxed controller generates no motion
  s.reset();
  s.command(1, 7, 0xffffff00);
  s.tick(0x000000f4); // 500 ms across millis wrap
  assert.equal(s.watchdog(), 1);
  s.command(0.5, 7, 0x100);
  assert.equal(s.watchdog(), 0);
  console.log('Firmware core: atomic targets, rate limit, watchdog, wrap, calibration and relax checks passed.');
})().catch(error => { console.error(error); process.exitCode = 1; });
