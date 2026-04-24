package com.kuroai.backend.controllers;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.*;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.client.RestTemplate;

import java.util.Map;

@CrossOrigin(origins = "*", maxAge = 3600)
@RestController
@RequestMapping("/api/manga")
public class MangaController {

    @Value("${kuroai.app.fastApiUrl}")
    private String fastApiUrl;

    private final RestTemplate restTemplate = new RestTemplate();

    /**
     * Proxies manga generation requests to the Python FastAPI backend.
     * The frontend calls Spring Boot → Spring Boot calls Python → returns result.
     */
    @PostMapping("/generate")
    public ResponseEntity<?> generateManga(@RequestBody Map<String, Object> request) {
        try {
            String url = fastApiUrl + "/api/generate";

            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);

            HttpEntity<Map<String, Object>> entity = new HttpEntity<>(request, headers);

            ResponseEntity<Map> response = restTemplate.exchange(
                    url, HttpMethod.POST, entity, Map.class);

            return ResponseEntity.ok(response.getBody());
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.SERVICE_UNAVAILABLE)
                    .body(Map.of(
                            "status", "error",
                            "message", "AI Generation service unavailable. Ensure Python backend is running on port 8000. Error: " + e.getMessage()
                    ));
        }
    }

    /**
     * Health check endpoint
     */
    @GetMapping("/health")
    public ResponseEntity<?> health() {
        return ResponseEntity.ok(Map.of("status", "ok", "service", "KuroAI Spring Boot Backend"));
    }
}
