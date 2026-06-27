package world

import (
	"testing"

	"bugfarmer/entities"
)

// recipeTestState: a player + a recipe table with one gated individual recipe and a 2-recipe
// "basic_furniture" book collection.
func recipeTestState() (*WorldState, *PlayerState) {
	state, p := shopTestState()
	state.Recipes = map[string]*entities.RecipeDef{
		"pickaxe_iron": {ID: "pickaxe_iron", Station: "anvil", Unlock: "default"},               // basic → auto
		"grandfather_clock": {ID: "grandfather_clock", Station: "sawmill", Unlock: "shop:carpenter"}, // gated individual
		"chair_wood": {ID: "chair_wood", Station: "workbench", Unlock: "shop:carpenter", Collection: "basic_furniture"},
		"table_wood": {ID: "table_wood", Station: "workbench", Unlock: "shop:carpenter", Collection: "basic_furniture"},
	}
	return state, p
}

func carpenterShop() *ShopData {
	return &ShopData{
		Kind:    "items",
		Recipes: []ShopEntry{{ID: "grandfather_clock", Price: 120}},
		Books:   []ShopEntry{{ID: "basic_furniture", Price: 200}},
	}
}

func TestShopBuyRecipe(t *testing.T) {
	state, p := recipeTestState()
	p.Coins = 150
	if !(&Match{}).shopBuyRecipe(nopDispatcher{}, state, "p1", p, carpenterShop(), "grandfather_clock") {
		t.Fatal("buying a listed gated recipe should succeed")
	}
	if p.Coins != 30 {
		t.Fatalf("coins: want 30, got %d", p.Coins)
	}
	if !p.KnownRecipes["grandfather_clock"] {
		t.Fatal("recipe should now be known")
	}
}

func TestShopBuyRecipeNoDoubleCharge(t *testing.T) {
	state, p := recipeTestState()
	p.Coins = 150
	(&Match{}).shopBuyRecipe(nopDispatcher{}, state, "p1", p, carpenterShop(), "grandfather_clock")
	if (&Match{}).shopBuyRecipe(nopDispatcher{}, state, "p1", p, carpenterShop(), "grandfather_clock") {
		t.Fatal("buying an already-known recipe must fail")
	}
	if p.Coins != 30 {
		t.Fatalf("must not be charged twice: got %d", p.Coins)
	}
}

func TestShopBuyRecipeNotListed(t *testing.T) {
	state, p := recipeTestState()
	p.Coins = 999
	// chair_wood is in a book, not the individual recipes list.
	if (&Match{}).shopBuyRecipe(nopDispatcher{}, state, "p1", p, carpenterShop(), "chair_wood") {
		t.Fatal("a recipe not in the shop's Recipes list must not be buyable individually")
	}
}

func TestShopBuyBookGrantsCollection(t *testing.T) {
	state, p := recipeTestState()
	p.Coins = 250
	if !(&Match{}).shopBuyBook(nopDispatcher{}, state, "p1", p, carpenterShop(), "basic_furniture") {
		t.Fatal("buying the book should succeed")
	}
	if p.Coins != 50 {
		t.Fatalf("coins: want 50, got %d", p.Coins)
	}
	if !p.KnownRecipes["chair_wood"] || !p.KnownRecipes["table_wood"] {
		t.Fatal("the whole collection should be learned from one book")
	}
	// Re-buying when all known is rejected, no charge.
	if (&Match{}).shopBuyBook(nopDispatcher{}, state, "p1", p, carpenterShop(), "basic_furniture") {
		t.Fatal("re-buying a fully-known book must fail")
	}
	if p.Coins != 50 {
		t.Fatalf("no double charge for a known book: got %d", p.Coins)
	}
}

func TestRecipeKnownGate(t *testing.T) {
	p := testPlayer(0, 0, "")
	p.KnownRecipes = map[string]bool{}
	basic := &entities.RecipeDef{Unlock: "default"}
	gated := &entities.RecipeDef{Unlock: "shop:carpenter"}
	if !recipeKnown(p, "pickaxe_iron", basic) {
		t.Fatal("basic/default recipes are always craftable")
	}
	if recipeKnown(p, "grandfather_clock", gated) {
		t.Fatal("a gated, unknown recipe must NOT be craftable")
	}
	p.KnownRecipes["grandfather_clock"] = true
	if !recipeKnown(p, "grandfather_clock", gated) {
		t.Fatal("a gated recipe becomes craftable once learned")
	}
}

func TestKnownRecipesPersistRoundTrip(t *testing.T) {
	p := testPlayer(0, 0, "")
	p.KnownRecipes = map[string]bool{"grandfather_clock": true, "chair_wood": true}
	slice := knownRecipesSlice(p)
	if len(slice) != 2 {
		t.Fatalf("slice should hold both ids, got %v", slice)
	}
	// rebuild as applyCharacterSave does
	rebuilt := make(map[string]bool, len(slice))
	for _, id := range slice {
		rebuilt[id] = true
	}
	if !rebuilt["grandfather_clock"] || !rebuilt["chair_wood"] || len(rebuilt) != 2 {
		t.Fatalf("round-trip lost recipes: %v", rebuilt)
	}
}
