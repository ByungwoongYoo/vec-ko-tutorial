// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Byungwoong Yoo
// Run: node verify-score-core.cjs [path/to/score-explainer.html]
// These checks use synthetic arithmetic and built-in Node modules.
'use strict';

const assert = require('node:assert/strict');
const crypto = require('node:crypto');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const htmlPath = path.resolve(process.argv[2] || path.join(__dirname, 'score-explainer.html'));
const html = fs.readFileSync(htmlPath, 'utf8');
const match = html.match(/<script\b(?=[^>]*\bid\s*=\s*["']score-core["'])[^>]*>([\s\S]*?)<\/script\s*>/i);
assert.ok(match, 'The HTML must contain a score-core script.');
const coreSource = match[1];
const moduleObject = { exports: {} };
vm.runInNewContext(coreSource, { module: moduleObject }, { timeout: 2000, filename: 'score-core.js' });
const core = moduleObject.exports;
let passed = 0;
let failed = 0;

function check(name, fn) {
  try {
    fn();
    passed += 1;
  } catch (error) {
    failed += 1;
    process.stderr.write(`FAIL: ${name}\n  ${error.message}\n`);
  }
}

function close(actual, expected, message) {
  assert.ok(Number.isFinite(actual), `${message}: expected a finite result, received ${actual}`);
  if (expected === 0) {
    assert.equal(actual, 0, `${message}: expected exactly zero, received ${actual}`);
    return;
  }
  const tolerance = 1e-12 * Math.abs(expected);
  assert.ok(Math.abs(actual - expected) <= tolerance,
    `${message}: expected ${expected}, received ${actual}`);
}

const EXPECTED_WEIGHTS = {
  T1: { de_score: 0.25, de_direction: 0.25, mmd_u: 0.30, variogram: 0.20 },
  T2: { de_score: 0.125, de_direction: 0.125, mmd_u: 0.15, variogram: 0.10,
    d2_shape: 1 / 12, occupancy_dice: 1 / 12, scale_log_ratio: 1 / 12, neighborhood_mmd: 0.25 },
  T3: { de_score: 0.30, de_direction: 0.25, severity_slope: 0.25, mmd_u: 0.12, variogram: 0.08 }
};
const HIGHER = new Set(['de_score', 'de_direction', 'occupancy_dice']);
const ABSOLUTE = new Set(['scale_log_ratio', 'severity_slope']);

// The expected constants follow the official per-task scoring tables.
// https://virtualembryo.ai/challenge/evaluation?section=scoring&task=1
// https://virtualembryo.ai/challenge/evaluation?section=scoring&task=2
// https://virtualembryo.ai/challenge/evaluation?section=scoring&task=3
function fixture(taskId, position = 'ceiling') {
  const values = {};
  for (const id of Object.keys(EXPECTED_WEIGHTS[taskId])) {
    let floor;
    let ceiling;
    let raw;
    if (ABSOLUTE.has(id)) {
      floor = -4;
      ceiling = 1;
      raw = { floor: -4, ceiling: 1, twiceDistance: 7, overshoot: 0 }[position];
    } else if (HIGHER.has(id)) {
      floor = 0;
      ceiling = 1;
      raw = { floor: 0, ceiling: 1, twiceDistance: -1, overshoot: 2 }[position];
    } else {
      floor = 1;
      ceiling = 0;
      raw = { floor: 1, ceiling: 0, twiceDistance: 2, overshoot: -1 }[position];
    }
    values[id] = { raw, floor, ceiling };
  }
  return values;
}

function metric(id, row) {
  return core.evaluateMetric(id, row);
}

function taskTotal(taskId, values, expected, label) {
  const result = core.evaluateTask(taskId, values);
  assert.equal(result.status, 'ok', `${label}: ${JSON.stringify(result.messages)}`);
  close(result.total, expected, label);
  close(result.metrics.reduce((sum, row) => sum + row.points, 0), expected, `${label}: row sum`);
  close(result.groups.reduce((sum, group) => sum + group.points, 0), expected, `${label}: group sum`);
}

for (const name of ['evaluateMetric', 'evaluateTask', 'parseScalar', 'evaluateBoundary', 'syntheticPreset']) {
  check(`export ${name}`, () => assert.equal(typeof core[name], 'function'));
}
check('TASKS export', () => assert.ok(core.TASKS && typeof core.TASKS === 'object'));

for (const taskId of Object.keys(EXPECTED_WEIGHTS)) {
  check(`${taskId}: exact metric set`, () => {
    const actual = core.TASKS[taskId].metrics.map(row => row.id).sort();
    assert.equal(JSON.stringify(actual), JSON.stringify(Object.keys(EXPECTED_WEIGHTS[taskId]).sort()));
  });
  for (const [id, weight] of Object.entries(EXPECTED_WEIGHTS[taskId])) {
    check(`${taskId}: fixed weight ${id}`, () => {
      const descriptor = core.TASKS[taskId].metrics.find(row => row.id === id);
      assert.ok(descriptor);
      assert.ok(Number.isFinite(descriptor.weight) && descriptor.weight >= 0);
      close(descriptor.weight, weight, `${taskId}/${id} weight`);
    });
  }
  check(`${taskId}: weights sum to one`, () => {
    close(core.TASKS[taskId].metrics.reduce((sum, row) => sum + row.weight, 0), 1, 'metric weights');
  });
  check(`${taskId}: group weights and membership`, () => {
    const task = core.TASKS[taskId];
    close(task.groups.reduce((sum, group) => sum + group.weight, 0), 1, 'group weights');
    for (const group of task.groups) {
      assert.ok(Number.isFinite(group.weight) && group.weight >= 0);
      const rows = task.metrics.filter(row => row.groupId === group.id);
      assert.equal(JSON.stringify(rows.map(row => row.id).sort()), JSON.stringify(Array.from(group.metricIds).sort()));
      close(rows.reduce((sum, row) => sum + row.withinWeight, 0), 1, 'within-group weights');
      for (const row of rows) {
        assert.ok(Number.isFinite(row.withinWeight) && row.withinWeight >= 0);
        close(row.weight, row.withinWeight * group.weight, 'effective metric weight');
        close(row.groupWeight, group.weight, 'metric group weight');
      }
    }
  });
  check(`${taskId}: task configuration is frozen`, () => {
    assert.ok(Object.isFrozen(core.TASKS));
    assert.ok(Object.isFrozen(core.TASKS[taskId]));
    assert.ok(Object.isFrozen(core.TASKS[taskId].metrics));
    assert.ok(core.TASKS[taskId].metrics.every(Object.isFrozen));
  });
  for (const [position, expected] of [
    ['floor', 50], ['ceiling', 100], ['twiceDistance', 100 / 3], ['overshoot', 100]
  ]) {
    check(`${taskId}: ${position} arithmetic`, () => taskTotal(taskId, fixture(taskId, position), expected, position));
  }
  for (const mode of ['floor', 'ceiling']) {
    check(`${taskId}: synthetic ${mode} preset`, () => {
      taskTotal(taskId, core.syntheticPreset(taskId, mode), mode === 'floor' ? 50 : 100, mode);
    });
  }
}

for (const id of ABSOLUTE) {
  for (const raw of [-2, 2]) {
    check(`${id}: folds raw ${raw} and both anchors`, () => {
      const result = metric(id, { raw, floor: -4, ceiling: 1 });
      assert.equal(result.status, 'ok');
      close(result.skill, 0.75, 'signed skill');
      close(result.transformed.raw, 2, 'folded raw');
      close(result.transformed.floor, 4, 'folded floor');
      close(result.transformed.ceiling, 1, 'folded ceiling');
    });
  }
  check(`${id}: equal absolute anchors rejected`, () => {
    assert.equal(metric(id, { raw: 0, floor: -2, ceiling: 2 }).status, 'error');
  });
  check(`${id}: reversed absolute anchors rejected`, () => {
    assert.equal(metric(id, { raw: 2, floor: -1, ceiling: 4 }).status, 'error');
  });
}

for (const [id, floor, ceiling] of [['de_score', 0, 1], ['mmd_u', 1, 0]]) {
  check(`${id}: equal anchors rejected`, () => {
    assert.equal(metric(id, { raw: 0.5, floor: 1, ceiling: 1 }).status, 'error');
  });
  check(`${id}: reversed anchors rejected`, () => {
    assert.equal(metric(id, { raw: 0.5, floor: ceiling, ceiling: floor }).status, 'error');
  });
  for (const invalid of [NaN, Infinity, -Infinity, 'wrong']) {
    check(`${id}: invalid floor ${String(invalid)}`, () => {
      assert.equal(metric(id, { raw: 0.5, floor: invalid, ceiling }).status, 'error');
    });
    check(`${id}: invalid ceiling ${String(invalid)}`, () => {
      assert.equal(metric(id, { raw: 0.5, floor, ceiling: invalid }).status, 'error');
    });
  }
  check(`${id}: empty anchor is incomplete`, () => {
    assert.equal(metric(id, { raw: 0.5, floor: '', ceiling }).status, 'incomplete');
  });
  check(`${id}: overshoot is clipped before division`, () => {
    const raw = id === 'de_score' ? 2 : -1;
    const result = metric(id, { raw, floor, ceiling });
    assert.equal(result.status, 'ok');
    close(result.skill, 1, 'overshoot skill');
  });
}

for (const [taskId, id, expected] of [
  ['T1', 'de_score', 75], ['T2', 'd2_shape', 100 * 11 / 12], ['T3', 'severity_slope', 75]
]) {
  check(`${taskId}: explicit missing ${id} keeps its weight`, () => {
    const values = fixture(taskId);
    values[id].raw = 'NaN';
    taskTotal(taskId, values, expected, 'missing weight');
    const row = core.evaluateTask(taskId, values).metrics.find(item => item.metric.id === id);
    assert.equal(row.status, 'missing');
    close(row.skill, 0, 'missing skill');
    close(row.points, 0, 'missing points');
  });
  check(`${taskId}: unentered ${id} blocks a total`, () => {
    const values = fixture(taskId);
    values[id].raw = '';
    const result = core.evaluateTask(taskId, values);
    assert.equal(result.status, 'incomplete');
    assert.equal(result.total, null);
  });
  check(`${taskId}: malformed ${id} blocks a total`, () => {
    const values = fixture(taskId);
    values[id].raw = '1abc';
    const result = core.evaluateTask(taskId, values);
    assert.equal(result.status, 'error');
    assert.equal(result.total, null);
  });
}

for (const [text, expected] of [
  ['0', 0], ['-2', -2], ['+2.5', 2.5], ['.5', 0.5], ['1.', 1], ['2e3', 2000], [' -2.5e-2 ', -0.025]
]) {
  check(`parse valid ${JSON.stringify(text)}`, () => {
    const result = core.parseScalar(text);
    assert.equal(result.status, 'valid');
    close(result.value, expected, 'parsed number');
  });
}
for (const text of ['', '   ']) {
  check(`parse unentered ${JSON.stringify(text)}`, () => {
    assert.equal(core.parseScalar(text, { allowMissing: true }).status, 'incomplete');
  });
  check(`parse explicitly allowed empty missing ${JSON.stringify(text)}`, () => {
    assert.equal(core.parseScalar(text, { allowMissing: true, allowEmptyMissing: true }).status, 'missing');
  });
}
for (const value of ['NaN', NaN, undefined, null]) {
  check(`parse explicit missing ${String(value)}`, () => {
    assert.equal(core.parseScalar(value, { allowMissing: true }).status, 'missing');
  });
}
check('NaN anchor cannot become valid', () => assert.equal(core.parseScalar('NaN').status, 'error'));
for (const value of ['1abc', '1_000', '0x10', '1,2', '1 2', 'Infinity', '+Infinity', '-Infinity', '∞', '1e309', Infinity, -Infinity, true, false, [], {}]) {
  check(`parse malformed or nonfinite ${JSON.stringify(value)}`, () => {
    assert.equal(core.parseScalar(value, { allowMissing: true }).status, 'error');
  });
}

for (const [label, id, row, expected] of [
  ['overflowing denominator at floor', 'mmd_u', { raw: 1e308, floor: 1e308, ceiling: 0 }, 0.5],
  ['overflowing denominator below floor', 'mmd_u', { raw: 1.5e308, floor: 1e308, ceiling: 0 }, 0.4],
  ['higher-direction large denominator', 'de_score', { raw: -1.5e308, floor: -1e308, ceiling: 0 }, 0.4],
  ['absolute large denominator', 'severity_slope', { raw: -1e308, floor: -1e308, ceiling: 0 }, 0.5],
  ['tiny positive skill remains nonzero', 'mmd_u', { raw: 1, floor: 1e-300, ceiling: 0 }, 1e-300],
  ['large finite ratio keeps a positive skill', 'mmd_u', { raw: 1e308, floor: 1, ceiling: 0 }, 1e-308],
  ['reciprocal branch supports an overflowing ratio', 'mmd_u', { raw: 1e308, floor: 1e-10, ceiling: 0 }, 1e-10 / 1e308],
  ['subnormal floor', 'mmd_u', { raw: Number.MIN_VALUE, floor: Number.MIN_VALUE, ceiling: 0 }, 0.5],
  ['subnormal distance', 'mmd_u', { raw: 2 * Number.MIN_VALUE, floor: Number.MIN_VALUE, ceiling: 0 }, 1 / 3]
]) {
  check(label, () => {
    const result = metric(id, row);
    assert.equal(result.status, 'ok', result.message);
    close(result.skill, expected, label);
    assert.ok(Number.isFinite(result.points), 'points must stay finite');
  });
}

// Unsupported arithmetic must be reported rather than shown as a valid zero.
for (const [label, id, row] of [
  ['nonfinite anchor distance', 'de_score', { raw: 0, floor: -Number.MAX_VALUE, ceiling: Number.MAX_VALUE }],
  ['nonfinite target distance', 'de_score', { raw: -Number.MAX_VALUE, floor: 0, ceiling: Number.MAX_VALUE }],
  ['positive skill would underflow to zero', 'mmd_u', { raw: Number.MAX_VALUE, floor: Number.MIN_VALUE, ceiling: 0 }]
]) {
  check(label, () => assert.equal(metric(id, row).status, 'error'));
}

const descriptor = core.TASKS.T1.metrics.find(row => row.id === 'de_score');
for (const [field, value] of [['weight', -1], ['weight', NaN], ['weight', Infinity],
  ['withinWeight', -1], ['withinWeight', NaN], ['groupWeight', -1], ['groupWeight', Infinity]]) {
  check(`metric weight safety: ${field}=${String(value)}`, () => {
    const result = core.evaluateMetric({ ...descriptor, [field]: value }, { raw: 0.5, floor: 0, ceiling: 1 });
    assert.equal(result.status, 'error');
  });
}
check('unknown metric rejected', () => assert.equal(metric('unknown', { raw: 0, floor: 0, ceiling: 1 }).status, 'error'));
check('unknown task rejected', () => assert.equal(core.evaluateTask('unknown', {}).status, 'error'));

// Each interval checks a numeric stage condition, not overall data eligibility.
// https://virtualembryo.ai/challenge/rules, section 10
const BOUNDARY_CASES = [
  ['extrapolation', 9.5, false], ['extrapolation', 9.500001, true],
  ['extrapolation', 13.499999, true], ['extrapolation', 13.5, true],
  ['extrapolation', 13.500001, false],
  ['heart', 8.25, false], ['heart', 8.250001, true], ['heart', 8.5, true],
  ['heart', 8.749999, true], ['heart', 8.75, false],
  ['embryo', 7.25, false], ['embryo', 7.250001, true], ['embryo', 7.5, true],
  ['embryo', 7.75, true], ['embryo', 7.999999, true], ['embryo', 8, false]
];
for (const [ruleId, stage, inside] of BOUNDARY_CASES) {
  check(`${ruleId}: E${stage} boundary`, () => {
    const result = core.evaluateBoundary(ruleId, stage);
    assert.equal(result.status, 'ok', result.message);
    assert.equal(result.inside, inside);
  });
}
check('unknown boundary rejected', () => assert.equal(core.evaluateBoundary('unknown', 8.5).status, 'error'));
check('genotype label cannot select a stage rule', () => assert.equal(core.evaluateBoundary('T3', 8.75).status, 'error'));
check('unentered stage is incomplete', () => assert.equal(core.evaluateBoundary('heart', '').status, 'incomplete'));
for (const stage of ['E8.5', '8.5abc', 'NaN', Infinity, -Infinity]) {
  check(`stage requires a finite numeric day: ${String(stage)}`, () => {
    assert.equal(core.evaluateBoundary('heart', stage).status, 'error');
  });
}
check('stage result contains no overall permission verdict', () => {
  const result = core.evaluateBoundary('heart', 8.25);
  assert.equal(result.status, 'ok');
  for (const name of ['eligible', 'approved', 'legal']) {
    assert.equal(Object.hasOwn(result, name), false);
  }
});

const sha256 = value => crypto.createHash('sha256').update(value).digest('hex');
process.stdout.write(`Synthetic checks: ${passed} passed, ${failed} failed.\n`);
process.stdout.write(`HTML SHA256: ${sha256(html)}\n`);
process.stdout.write(`score-core SHA256: ${sha256(coreSource)}\n`);
process.exitCode = failed ? 1 : 0;
