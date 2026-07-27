/**
 * Example Go code with various code smells
 * Used for testing detection rules
 */

package MyPackage // GO010: Package name should be lowercase

import (
    "fmt"
    "os" // GO004: Unused import (if not used)
)

// GO001: Missing error handling
func ReadFile(path string) []byte {
    data, _ := os.ReadFile(path) // Ignoring error!
    return data
}

// GO002: Missing defer cleanup
func OpenFile() []byte {
    file, err := os.Open("file.txt")
    if err != nil {
        return nil
    }
    // Never closed!
    data, _ := os.ReadFile("file.txt")
    return data
}

// GO005: Missing nil check
func ProcessObject(obj *MyStruct) {
    result := obj.Calculate() // No nil check!
}

// GO006: Unchecked type assertion
func GetValue(i interface{}) {
    value := i.(MyType) // No ok check!
    fmt.Println(value)
}

// GO007: Channel leak
func StartWorker() {
    ch := make(chan int)
    go func() {
        ch <- 42
    }()
    // Channel never closed!
}

// GO008: Goroutine leak
func StartAsync() {
    go func() {
        fmt.Println("async work")
    }()
    // No synchronization!
}

// GO009: Potential race condition
var globalCounter int // No mutex protection!

func IncrementCounter() {
    go func() {
        globalCounter++
    }()
    go func() {
        globalCounter++
    }()
}

// GO003: Interface compliance not verified
type MyInterface interface {
    Method1() string
    Method2() int
}

type MyStruct struct {
    name string
    id   int
}

func (m *MyStruct) Method1() string {
    return m.name
}

func (m *MyStruct) Method2() int {
    return m.id
}

// Should verify: var _ MyInterface = (*MyStruct)(nil)

// Better examples with proper error handling

// GO001: Proper error handling
func ReadFileCorrectly(path string) ([]byte, error) {
    data, err := os.ReadFile(path)
    if err != nil {
        return nil, err
    }
    return data, nil
}

// GO002: Proper defer cleanup
func OpenFileCorrectly() ([]byte, error) {
    file, err := os.Open("file.txt")
    if err != nil {
        return nil, err
    }
    defer file.Close() // Proper cleanup!

    // Read file...
    return nil, nil
}

// GO005: Proper nil check
func ProcessObjectCorrectly(obj *MyStruct) {
    if obj == nil {
        return
    }
    result := obj.Calculate()
}

// GO006: Proper type assertion
func GetValueCorrectly(i interface{}) {
    value, ok := i.(MyType)
    if !ok {
        return
    }
    fmt.Println(value)
}

// GO007: Proper channel closure
func StartWorkerCorrectly() {
    ch := make(chan int)
    go func() {
        ch <- 42
        close(ch) // Proper cleanup!
    }()
}

// GO008: Proper goroutine synchronization
func StartAsyncCorrectly() {
    var wg sync.WaitGroup
    wg.Add(1)
    go func() {
        defer wg.Done()
        fmt.Println("async work")
    }()
    wg.Wait()
}

// GO009: Proper race condition prevention
var (
    mu            sync.Mutex
    safeCounter   int // Protected by mutex
)

func IncrementCounterSafely() {
    var wg sync.WaitGroup
    wg.Add(2)

    go func() {
        defer wg.Done()
        mu.Lock()
        safeCounter++
        mu.Unlock()
    }()

    go func() {
        defer wg.Done()
        mu.Lock()
        safeCounter++
        mu.Unlock()
    }()

    wg.Wait()
}

// GO003: Interface compliance verified
type ProperInterface interface {
    Method1() string
    Method2() int
}

type ProperStruct struct {
    name string
    id   int
}

func (p *ProperStruct) Method1() string {
    return p.name
}

func (p *ProperStruct) Method2() int {
    return p.id
}

// Verify interface compliance at compile time
var _ ProperInterface = (*ProperStruct)(nil)

// GO010: Proper package naming
// Package name should be: package mypakage (lowercase)
