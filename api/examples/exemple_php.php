<?php
/**
 * 🏥 Hospitalidée IA API - Exemple PHP
 * ===================================
 * 
 * Exemple d'intégration de l'API Hospitalidée IA en PHP.
 * Montre comment utiliser l'API pour analyser des avis patients.
 * 
 * Usage:
 *     php exemple_php.php
 * 
 * Prérequis:
 *     - PHP 7.4+
 *     - Extension curl activée
 *     - Extension json activée
 */

class HospitalideeIA 
{
    private $apiUrl;
    private $timeout;
    
    /**
     * Initialise le client API
     * 
     * @param string $apiUrl URL de base de l'API
     *                      'http://localhost:8000'        → 💻 Tests en local
     *                      'http://VOTRE_IP_VPS:8000'     → 🌐 VPS production
     *                      'https://api.votre-site.com'   → 🔒 VPS avec domaine SSL
     * @param int $timeout Timeout en secondes
     */
    public function __construct($apiUrl = 'http://localhost:8000', $timeout = 60) 
    {
        $this->apiUrl = rtrim($apiUrl, '/');
        $this->timeout = $timeout;
    }
    
    /**
     * Évalue un avis patient de manière complète
     * 
     * @param string $typeEvaluation "etablissement" ou "medecin"
     * @param string $avisText Texte de l'avis patient
     * @param array|null $questionnaireEtablissement Notes établissement
     * @param array|null $questionnaireMedecin Évaluations médecin
     * @param bool $genererTitre Générer un titre suggéré
     * @param bool $analyseDetaillee Inclure l'analyse détaillée
     * @return array Résultat complet de l'évaluation
     * @throws Exception En cas d'erreur API
     */
    public function evaluerAvisComplet(
        $typeEvaluation, 
        $avisText, 
        $questionnaireEtablissement = null, 
        $questionnaireMedecin = null,
        $genererTitre = true,
        $analyseDetaillee = true
    ) {
        $data = [
            'type_evaluation' => $typeEvaluation,
            'avis_text' => $avisText,
            'generer_titre' => $genererTitre,
            'analyse_detaillee' => $analyseDetaillee
        ];
        
        // Ajouter le questionnaire approprié
        if ($typeEvaluation === 'etablissement') {
            if (!$questionnaireEtablissement) {
                throw new Exception("questionnaire_etablissement requis pour type 'etablissement'");
            }
            $data['questionnaire_etablissement'] = $questionnaireEtablissement;
        } elseif ($typeEvaluation === 'medecin') {
            if (!$questionnaireMedecin) {
                throw new Exception("questionnaire_medecin requis pour type 'medecin'");
            }
            $data['questionnaire_medecin'] = $questionnaireMedecin;
        } else {
            throw new Exception("type_evaluation doit être 'etablissement' ou 'medecin'");
        }
        
        return $this->post('/evaluate', $data);
    }
    
    /**
     * Analyse uniquement le sentiment d'un texte
     * 
     * @param string $text Texte à analyser
     * @return array Analyse de sentiment
     */
    public function analyserSentimentSeul($text) 
    {
        return $this->post('/sentiment', $text);
    }
    
    /**
     * Vérifie que l'API fonctionne
     * 
     * @return array Status de l'API
     */
    public function verifierSante() 
    {
        return $this->get('/health');
    }
    
    /**
     * Effectue une requête GET
     * 
     * @param string $endpoint Endpoint de l'API
     * @return array Réponse décodée
     * @throws Exception En cas d'erreur
     */
    private function get($endpoint) 
    {
        $url = $this->apiUrl . $endpoint;
        
        $ch = curl_init();
        curl_setopt_array($ch, [
            CURLOPT_URL => $url,
            CURLOPT_RETURNTRANSFER => true,
            CURLOPT_TIMEOUT => $this->timeout,
            CURLOPT_HTTPHEADER => [
                'User-Agent: HospitalideeIA-PHP-Client/1.0'
            ]
        ]);
        
        $response = curl_exec($ch);
        $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        $error = curl_error($ch);
        curl_close($ch);
        
        if ($error) {
            throw new Exception("Erreur cURL GET $endpoint: $error");
        }
        
        if ($httpCode >= 400) {
            throw new Exception("Erreur HTTP GET $endpoint: $httpCode");
        }
        
        $decoded = json_decode($response, true);
        if (json_last_error() !== JSON_ERROR_NONE) {
            throw new Exception("Erreur JSON GET $endpoint: " . json_last_error_msg());
        }
        
        return $decoded;
    }
    
    /**
     * Effectue une requête POST
     * 
     * @param string $endpoint Endpoint de l'API
     * @param mixed $data Données à envoyer
     * @return array Réponse décodée
     * @throws Exception En cas d'erreur
     */
    private function post($endpoint, $data) 
    {
        $url = $this->apiUrl . $endpoint;
        $jsonData = json_encode($data);
        
        if (json_last_error() !== JSON_ERROR_NONE) {
            throw new Exception("Erreur encodage JSON: " . json_last_error_msg());
        }
        
        $ch = curl_init();
        curl_setopt_array($ch, [
            CURLOPT_URL => $url,
            CURLOPT_RETURNTRANSFER => true,
            CURLOPT_POST => true,
            CURLOPT_POSTFIELDS => $jsonData,
            CURLOPT_TIMEOUT => $this->timeout,
            CURLOPT_HTTPHEADER => [
                'Content-Type: application/json',
                'User-Agent: HospitalideeIA-PHP-Client/1.0'
            ]
        ]);
        
        $response = curl_exec($ch);
        $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        $error = curl_error($ch);
        curl_close($ch);
        
        if ($error) {
            throw new Exception("Erreur cURL POST $endpoint: $error");
        }
        
        $decoded = json_decode($response, true);
        if (json_last_error() !== JSON_ERROR_NONE) {
            throw new Exception("Erreur JSON POST $endpoint: " . json_last_error_msg());
        }
        
        if ($httpCode >= 400) {
            $errorMsg = isset($decoded['detail']) ? $decoded['detail'] : "HTTP $httpCode";
            throw new Exception("Erreur API POST $endpoint: $errorMsg");
        }
        
        return $decoded;
    }
}

/**
 * Exemple d'évaluation d'un établissement
 */
function exempleEtablissement() 
{
    echo "🏥 EXEMPLE: Évaluation Établissement\n";
    echo str_repeat("=", 50) . "\n";
    
    $client = new HospitalideeIA();
    
    $avisText = "
    Séjour globalement satisfaisant dans cet hôpital. Le personnel était très 
    professionnel et attentif, particulièrement les infirmières de nuit qui ont 
    été formidables. Les médecins ont pris le temps d'expliquer les traitements 
    et ont répondu à toutes mes questions.
    
    Seul bémol: l'attente aux urgences était un peu longue (3h) et les repas 
    auraient pu être un peu plus variés. Mais globalement, je recommande cet 
    établissement pour la qualité des soins.
    ";
    
    $questionnaire = [
        'medecins' => 4,
        'personnel' => 5,
        'accueil' => 3,
        'prise_en_charge' => 4,
        'confort' => 3
    ];
    
    try {
        echo "📤 Envoi de l'évaluation...\n";
        $startTime = microtime(true);
        
        $result = $client->evaluerAvisComplet(
            'etablissement',
            $avisText,
            $questionnaire
        );
        
        $duration = microtime(true) - $startTime;
        
        echo "✅ Évaluation terminée!\n";
        printf("⏱️  Durée: %.1fs\n", $duration);
        echo "\n";
        
        // Affichage des résultats
        echo "📊 RÉSULTATS:\n";
        printf("Note finale: %.1f/5\n", $result['note_finale']);
        printf("Sentiment: %s\n", $result['sentiment']);
        printf("Confiance: %.0f%%\n", $result['confiance'] * 100);
        printf("Intensité émotionnelle: %.0f%%\n", $result['intensite_emotionnelle'] * 100);
        
        if (!empty($result['titre_suggere'])) {
            printf("Titre suggéré: \"%s\"\n", $result['titre_suggere']);
        }
        
        if (!empty($result['mode_degrade'])) {
            echo "⚠️  Mode dégradé activé (IA limitée)\n";
        }
        
        echo "\n";
        
        // Analyse détaillée si disponible
        if (!empty($result['analyse_detaillee'])) {
            $analyse = $result['analyse_detaillee'];
            echo "🔍 ANALYSE DÉTAILLÉE:\n";
            
            if (!empty($analyse['questionnaire'])) {
                $q = $analyse['questionnaire'];
                printf("Note questionnaire: %.1f/5\n", $q['note']);
                echo "Détails: " . json_encode($q['details']) . "\n";
            }
            
            if (!empty($analyse['sentiment'])) {
                $s = $analyse['sentiment'];
                printf("Sentiment IA: %s\n", $s['sentiment'] ?? 'N/A');
                printf("Confiance IA: %.0f%%\n", ($s['confidence'] ?? 0) * 100);
                
                if (!empty($s['positive_indicators'])) {
                    echo "Indicateurs positifs: " . implode(', ', array_slice($s['positive_indicators'], 0, 3)) . "\n";
                }
                
                if (!empty($s['negative_indicators'])) {
                    echo "Indicateurs négatifs: " . implode(', ', array_slice($s['negative_indicators'], 0, 3)) . "\n";
                }
            }
        }
        
        return $result;
        
    } catch (Exception $e) {
        echo "❌ Erreur: " . $e->getMessage() . "\n";
        return null;
    }
}

/**
 * Exemple d'évaluation d'un médecin
 */
function exempleMedecin() 
{
    echo "\n👨‍⚕️ EXEMPLE: Évaluation Médecin\n";
    echo str_repeat("=", 50) . "\n";
    
    $client = new HospitalideeIA();
    
    $avisText = "
    Dr Martin est un médecin exceptionnel. Dès notre première rencontre, j'ai 
    été impressionné par sa capacité d'écoute et sa bienveillance. Il prend 
    vraiment le temps d'expliquer les traitements de façon claire et 
    compréhensible.
    
    Je me sens en totale confiance avec lui. Ses prescriptions sont toujours 
    très motivées et il respecte complètement mes choix et mes contraintes. 
    Je le recommande vivement !
    ";
    
    $questionnaire = [
        'explications' => 'Excellentes',
        'confiance' => 'Confiance totale',
        'motivation' => 'Très motivé',
        'respect' => 'Très respectueux'
    ];
    
    try {
        echo "📤 Envoi de l'évaluation...\n";
        
        $result = $client->evaluerAvisComplet(
            'medecin',
            $avisText,
            null,
            $questionnaire
        );
        
        echo "✅ Évaluation terminée!\n";
        echo "\n";
        
        echo "📊 RÉSULTATS:\n";
        printf("Note finale: %.1f/5\n", $result['note_finale']);
        printf("Sentiment: %s\n", $result['sentiment']);
        printf("Confiance: %.0f%%\n", $result['confiance'] * 100);
        
        if (!empty($result['titre_suggere'])) {
            printf("Titre suggéré: \"%s\"\n", $result['titre_suggere']);
        }
        
        return $result;
        
    } catch (Exception $e) {
        echo "❌ Erreur: " . $e->getMessage() . "\n";
        return null;
    }
}

/**
 * Exemple d'analyse de sentiment uniquement
 */
function exempleSentimentSeul() 
{
    echo "\n😊 EXEMPLE: Analyse Sentiment Seule\n";
    echo str_repeat("=", 50) . "\n";
    
    $client = new HospitalideeIA();
    
    $texts = [
        "Personnel très gentil et professionnel",
        "Attente beaucoup trop longue, très décevant",
        "Correct dans l'ensemble, sans plus",
        "Absolument parfait, je recommande vivement !"
    ];
    
    foreach ($texts as $i => $text) {
        try {
            printf("📝 Texte %d: \"%s\"\n", $i + 1, $text);
            
            $result = $client->analyserSentimentSeul($text);
            
            if ($result['status'] === 'success') {
                $data = $result['data'];
                $sentiment = $data['sentiment'] ?? 'inconnu';
                $confidence = $data['confidence'] ?? 0;
                
                $sentimentEmojis = [
                    'positif' => '😊',
                    'negatif' => '😞',
                    'neutre' => '😐'
                ];
                $emoji = $sentimentEmojis[$sentiment] ?? '❓';
                
                printf("   → %s %s (confiance: %.0f%%)\n", $emoji, $sentiment, $confidence * 100);
            } else {
                printf("   → ❌ Erreur: %s\n", $result['message'] ?? 'Inconnue');
            }
            
            echo "\n";
            
        } catch (Exception $e) {
            printf("   → ❌ Erreur: %s\n", $e->getMessage());
            echo "\n";
        }
    }
}

/**
 * Teste la connexion à l'API
 */
function testConnexion() 
{
    echo "🔍 TEST DE CONNEXION\n";
    echo str_repeat("=", 50) . "\n";
    
    $client = new HospitalideeIA();
    
    try {
        $health = $client->verifierSante();
        
        if (($health['status'] ?? '') === 'healthy') {
            echo "✅ API accessible et fonctionnelle\n";
            
            $config = $health['config'] ?? [];
            printf("   Modèle Mistral: %s\n", $config['modele_mistral'] ?? 'N/A');
            printf("   Version: %s\n", $config['version'] ?? 'N/A');
            
            $services = $health['services'] ?? [];
            foreach ($services as $service => $status) {
                $emoji = ($status === 'ok') ? '✅' : '❌';
                printf("   %s: %s %s\n", $service, $emoji, $status);
            }
            
            return true;
        } else {
            echo "⚠️  API accessible mais en mode dégradé\n";
            printf("   Status: %s\n", $health['status'] ?? 'inconnu');
            return false;
        }
        
    } catch (Exception $e) {
        printf("❌ API non accessible: %s\n", $e->getMessage());
        echo "\n";
        echo "🔧 Vérifications:\n";
        echo "   • L'API est-elle démarrée ?\n";
        echo "   • Le port 8000 est-il ouvert ?\n";
        echo "   • URL correcte ? (défaut: http://localhost:8000)\n";
        return false;
    }
}

/**
 * Fonction principale - exécute tous les exemples
 */
function main() 
{
    echo "🏥 Hospitalidée IA API - Exemples PHP\n";
    echo str_repeat("=", 60) . "\n";
    echo "\n";
    echo "💡 Pour VPS, changez l'URL dans le constructeur HospitalideeIA:\n";
    echo "   http://localhost:8000        → 💻 Tests en local\n";
    echo "   http://VOTRE_IP_VPS:8000     → 🌐 VPS production\n";
    echo "   https://api.votre-site.com   → 🔒 VPS avec domaine SSL\n";
    echo "\n";
    
    // Test de connexion
    if (!testConnexion()) {
        echo "\n❌ Impossible de continuer sans connexion API\n";
        return;
    }
    
    echo "\n" . str_repeat("=", 60) . "\n";
    
    // Exemples d'utilisation
    try {
        // Évaluation établissement
        $resultEtab = exempleEtablissement();
        
        // Évaluation médecin
        $resultMed = exempleMedecin();
        
        // Analyse sentiment seule
        exempleSentimentSeul();
        
        echo str_repeat("=", 60) . "\n";
        echo "🎉 Tous les exemples ont été exécutés avec succès !\n";
        echo "\n";
        echo "💡 Intégration dans votre code:\n";
        echo "   1. Vérifiez que curl et json sont activés\n";
        echo "   2. Copiez la classe HospitalideeIA\n";
        echo "   3. Utilisez \$client->evaluerAvisComplet()\n";
        echo "\n";
        echo "📖 Documentation complète: http://localhost:8000/docs\n";
        
    } catch (Exception $e) {
        printf("\n❌ Erreur générale: %s\n", $e->getMessage());
    }
}

// Exécution si appelé directement
if (php_sapi_name() === 'cli') {
    main();
}
?>