/**
 * Example TypeScript code with various code smells
 * Used for testing detection rules
 */

// TS001: Usage of 'any' type
function processAny(data: any) {
    return data.value;
}

// TS003: Implicit any (parameters without type)
function addNumbers(a, b) {
    return a + b;
}

// TS002: Unused variable
function unusedVariable() {
    const unused = 42;
    const used = 100;
    return used;
}

// TS005: Long function
function veryLongFunction() {
    const x = 1;
    const y = 2;
    const z = 3;
    const a = 4;
    const b = 5;
    const c = 6;
    const d = 7;
    const e = 8;
    const f = 9;
    const g = 10;
    const h = 11;
    const i = 12;
    const j = 13;
    const k = 14;
    const l = 15;
    const m = 16;
    const n = 17;
    const o = 18;
    const p = 19;
    const q = 20;
    const r = 21;
    const s = 22;
    const t = 23;
    const u = 24;
    const v = 25;
    console.log(x + y + z);
}

// TS008: Complex conditional
function complexCondition(a: number, b: number, c: number, d: number) {
    if (a > 0 && b < 10 && c === 5 && d !== 0 ? a : b) {
        return true;
    }
    return false;
}

// TS009: console.log in production
function debug() {
    console.log('debug info');
    console.log('more debug');
    console.log('even more');
}

// TS010: Missing return type
function getValue() {
    return 42;
}

// TS011: Too many parameters
function tooManyParams(a: string, b: number, c: boolean, d: string, e: number, f: string) {
    return a + b + c + d + e + f;
}

// TS012: Explicit any without comment
const anyValue: any = {};
const anotherAny: any = [];

// TS013: Type assertion
interface User {
    name: string;
    age: number;
}

function getUser() {
    const user = {} as User; // Type assertion
    return user;
}

// TS014: Non-null assertion
function processUser(user: User | null) {
    const name = user!.name; // Non-null assertion
    return name.toUpperCase();
}

// TS015: Dead code (commented)
function exampleFunction() {
    // console.log('old debug code');
    // if (someCondition) { doSomething(); }
    // deprecated API call
}

// TS004: Promise without .catch()
function fetchData() {
    fetch('/api/data')
        .then(response => response.json());
}

// TS006: Missing null check
interface Optional {
    method?: () => void;
}

function callMethod(obj: Optional) {
    obj.method?.(); // Optional chaining, could be better
}

// TS007: Unused import
import * as fs from 'fs';
import * as path from 'path';

// Only fs is used
export function readConfig(file: string) {
    return fs.readFileSync(file, 'utf-8');
}
