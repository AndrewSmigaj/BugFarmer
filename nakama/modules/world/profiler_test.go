package world

import "testing"

// The authority's snapshot upload is counted per game-day (total, count, fattest one) and cleared at the rollover;
// a profiler that is off counts nothing (production pays nothing).
func TestPerfSnapshotUploadBytes(t *testing.T) {
	p := NewPerfStats(true)
	p.AddSnapshotInBytes(1200)
	p.AddSnapshotInBytes(5000)
	p.AddSnapshotInBytes(300)
	if p.snapInBytes != 6500 || p.snapInMsgs != 3 || p.snapInMax != 5000 {
		t.Fatalf("snapshot bytes=%d msgs=%d max=%d, want 6500/3/5000", p.snapInBytes, p.snapInMsgs, p.snapInMax)
	}
	p.reset()
	if p.snapInBytes != 0 || p.snapInMsgs != 0 || p.snapInMax != 0 {
		t.Fatalf("reset left snapshot bytes=%d msgs=%d max=%d", p.snapInBytes, p.snapInMsgs, p.snapInMax)
	}

	off := NewPerfStats(false)
	off.AddSnapshotInBytes(1200)
	if off.snapInBytes != 0 || off.snapInMsgs != 0 {
		t.Fatalf("a disabled profiler counted %d bytes", off.snapInBytes)
	}
	var none *PerfStats
	none.AddSnapshotInBytes(10) // nil-safe, like every other method
}
