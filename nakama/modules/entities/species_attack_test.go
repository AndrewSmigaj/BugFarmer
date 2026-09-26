package entities

import "testing"

// The data-driven attack profile: an explicit attack{} block wins; a legacy species with only the top-level
// attack_* fields gets a synthesized profile so nothing loses its attack in the migration.

func TestNormalizeAttack_ExplicitBlockPreserved(t *testing.T) {
	s := &BugSpecies{AttackDamage: 1, Attack: &AttackConfig{Style: "contact", Damage: 3, TelegraphSecs: 0.45}}
	s.normalizeAttack()
	if s.Attack.Damage != 3 || s.Attack.TelegraphSecs != 0.45 {
		t.Fatalf("explicit attack{} must be preserved untouched, got %+v", s.Attack)
	}
}

func TestNormalizeAttack_LegacyContactSynth(t *testing.T) {
	s := &BugSpecies{Category: "swarm", AttackDamage: 2, AttackCooldown: 1.6, AttackIsSting: true, StingsOnlyDefending: true}
	s.normalizeAttack()
	if s.Attack == nil {
		t.Fatal("a legacy attacker must get a synthesized Attack")
	}
	if s.Attack.Style != "contact" || s.Attack.Damage != 2 || s.Attack.CooldownSecs != 1.6 ||
		!s.Attack.IsSting || !s.Attack.OnlyDefending {
		t.Fatalf("bad contact synth: %+v", s.Attack)
	}
}

func TestNormalizeAttack_NonAttackerStaysNil(t *testing.T) {
	s := &BugSpecies{AttackDamage: 0}
	s.normalizeAttack()
	if s.Attack != nil {
		t.Fatalf("a non-attacker must stay Attack==nil, got %+v", s.Attack)
	}
}
