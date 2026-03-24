package com.stockprediction.service;

import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;
import java.util.Map;
import java.util.HashMap;

@Service
public class PredictionService {

    // URL of the Python FastAPI ML Service
    private final String mlServiceUrl = "http://localhost:8000/predict";
    
    // In a real application, we would use RestTemplate to call the ML Service
    // private final RestTemplate restTemplate = new RestTemplate();

    public Map<String, Object> getPrediction(String symbol) {
        // Construct request body for ML service
        Map<String, String> request = new HashMap<>();
        request.put("symbol", symbol);
        request.put("startDate", "2023-01-01");
        request.put("endDate", "2024-01-01");
        
        // Simulating the response from Python ML Service
        // Map<String, Object> response = restTemplate.postForObject(mlServiceUrl, request, Map.class);
        
        // Mock response for now
        Map<String, Object> mockResponse = new HashMap<>();
        mockResponse.put("symbol", symbol);
        mockResponse.put("prediction", "UP");
        mockResponse.put("confidence", 0.85);
        mockResponse.put("decision", "BUY");
        mockResponse.put("source", "Java Backend via ML Service Mock");
        
        return mockResponse;
    }
}
