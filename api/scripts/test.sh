#!/bin/bash
# ============================================
# 🏥 Hospitalidée IA API - Script de test
# ============================================
# Teste que l'API fonctionne correctement

set -e

echo "🧪 Tests Hospitalidée IA API..."
echo "================================"

API_URL="http://localhost:8000"
TOTAL_TESTS=0
PASSED_TESTS=0

# Fonction de test
run_test() {
    local test_name="$1"
    local test_command="$2"
    local expected_status="$3"
    
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    echo -n "🔍 Test: $test_name... "
    
    if eval "$test_command" > /dev/null 2>&1; then
        if [ "$expected_status" = "success" ]; then
            echo "✅ PASSÉ"
            PASSED_TESTS=$((PASSED_TESTS + 1))
        else
            echo "❌ ÉCHEC (succès inattendu)"
        fi
    else
        if [ "$expected_status" = "fail" ]; then
            echo "✅ PASSÉ (échec attendu)"
            PASSED_TESTS=$((PASSED_TESTS + 1))
        else
            echo "❌ ÉCHEC"
        fi
    fi
}

# Fonction pour tester une requête JSON
test_json_endpoint() {
    local test_name="$1"
    local endpoint="$2"
    local data="$3"
    local expected_field="$4"
    
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    echo -n "🔍 Test: $test_name... "
    
    response=$(curl -s -X POST "$API_URL$endpoint" \
        -H "Content-Type: application/json" \
        -d "$data" || echo "CURL_ERROR")
    
    if [ "$response" = "CURL_ERROR" ]; then
        echo "❌ ÉCHEC (erreur connexion)"
        return
    fi
    
    if echo "$response" | grep -q "$expected_field"; then
        echo "✅ PASSÉ"
        PASSED_TESTS=$((PASSED_TESTS + 1))
    else
        echo "❌ ÉCHEC (champ '$expected_field' non trouvé)"
        echo "   Réponse: $(echo "$response" | head -c 100)..."
    fi
}

echo ""
echo "🏥 Tests de base de l'API..."

# Test 1: Health check
run_test "Health check" "curl -f -s $API_URL/health" "success"

# Test 2: Page d'accueil
run_test "Page d'accueil" "curl -f -s $API_URL/" "success"

# Test 3: Documentation Swagger
run_test "Documentation Swagger" "curl -f -s $API_URL/docs" "success"

# Test 4: Documentation ReDoc
run_test "Documentation ReDoc" "curl -f -s $API_URL/redoc" "success"

echo ""
echo "🎯 Tests des endpoints principaux..."

# Test 5: Évaluation établissement
test_json_endpoint "Évaluation établissement" "/evaluate" '{
    "type_evaluation": "etablissement",
    "avis_text": "Séjour excellent dans cet hôpital. Le personnel était très attentif et professionnel. Les médecins ont pris le temps d'\''expliquer les traitements.",
    "questionnaire_etablissement": {
        "medecins": 5,
        "personnel": 5,
        "accueil": 4,
        "prise_en_charge": 4,
        "confort": 3
    }
}' "note_finale"

# Test 6: Évaluation médecin
test_json_endpoint "Évaluation médecin" "/evaluate" '{
    "type_evaluation": "medecin",
    "avis_text": "Dr Martin est formidable. Explications très claires et rassurantes. Je recommande vivement.",
    "questionnaire_medecin": {
        "explications": "Excellentes",
        "confiance": "Confiance totale",
        "motivation": "Très motivé",
        "respect": "Très respectueux"
    }
}' "note_finale"

# Test 7: Analyse sentiment seule
test_json_endpoint "Analyse sentiment" "/sentiment" '"Personnel très gentil et professionnel"' "sentiment"

echo ""
echo "⚠️ Tests d'erreurs (doivent échouer)..."

# Test 8: Évaluation sans questionnaire
TOTAL_TESTS=$((TOTAL_TESTS + 1))
echo -n "🔍 Test: Évaluation sans questionnaire... "
response=$(curl -s -X POST "$API_URL/evaluate" \
    -H "Content-Type: application/json" \
    -d '{
        "type_evaluation": "etablissement",
        "avis_text": "Test sans questionnaire"
    }' || echo "CURL_ERROR")

if echo "$response" | grep -q "400"; then
    echo "✅ PASSÉ (erreur 400 attendue)"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    echo "❌ ÉCHEC (erreur 400 attendue)"
fi

# Test 9: Texte trop court
TOTAL_TESTS=$((TOTAL_TESTS + 1))
echo -n "🔍 Test: Texte trop court... "
response=$(curl -s -X POST "$API_URL/evaluate" \
    -H "Content-Type: application/json" \
    -d '{
        "type_evaluation": "etablissement",
        "avis_text": "Court",
        "questionnaire_etablissement": {
            "medecins": 3, "personnel": 3, "accueil": 3,
            "prise_en_charge": 3, "confort": 3
        }
    }' || echo "CURL_ERROR")

if echo "$response" | grep -q "422\|400"; then
    echo "✅ PASSÉ (erreur de validation attendue)"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    echo "❌ ÉCHEC (erreur de validation attendue)"
fi

echo ""
echo "🔬 Test de charge léger..."

# Test 10: 3 requêtes rapides
TOTAL_TESTS=$((TOTAL_TESTS + 1))
echo -n "🔍 Test: 3 requêtes consécutives... "

SUCCESS_COUNT=0
for i in {1..3}; do
    response=$(curl -s -w "%{http_code}" -X POST "$API_URL/evaluate" \
        -H "Content-Type: application/json" \
        -d "{
            \"type_evaluation\": \"etablissement\",
            \"avis_text\": \"Test de charge numéro $i - personnel correct\",
            \"questionnaire_etablissement\": {
                \"medecins\": 3, \"personnel\": 3, \"accueil\": 3,
                \"prise_en_charge\": 3, \"confort\": 3
            }
        }" || echo "000")
    
    if echo "$response" | grep -q "200"; then
        SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
    fi
    sleep 1
done

if [ $SUCCESS_COUNT -eq 3 ]; then
    echo "✅ PASSÉ (3/3 requêtes réussies)"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    echo "❌ ÉCHEC ($SUCCESS_COUNT/3 requêtes réussies)"
fi

# Résultats finaux
echo ""
echo "📊 RÉSULTATS DES TESTS"
echo "======================"
echo "Tests passés: $PASSED_TESTS/$TOTAL_TESTS"

if [ $PASSED_TESTS -eq $TOTAL_TESTS ]; then
    echo "🎉 TOUS LES TESTS PASSENT !"
    echo ""
    echo "✅ Votre API Hospitalidée IA fonctionne parfaitement"
    echo ""
    echo "🚀 Prêt pour la production !"
    echo "  • API: $API_URL"
    echo "  • Documentation: $API_URL/docs"
    echo ""
    exit 0
else
    echo "⚠️ $(($TOTAL_TESTS - $PASSED_TESTS)) test(s) ont échoué"
    echo ""
    echo "🔧 Vérifications suggérées:"
    echo "  • L'API est-elle démarrée ? curl $API_URL/health"
    echo "  • La clé Mistral est-elle configurée dans .env ?"
    echo "  • Consultez les logs: docker-compose logs"
    echo ""
    exit 1
fi