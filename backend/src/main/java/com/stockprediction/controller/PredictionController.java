package com.stockprediction.controller;

import com.stockprediction.service.PredictionService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/api/prediction")
@CrossOrigin(origins = "*") // Allow frontend access
public class PredictionController {

    private final PredictionService predictionService;

    @Autowired
    public PredictionController(PredictionService predictionService) {
        this.predictionService = predictionService;
    }

    @GetMapping("/predict")
    public Map<String, Object> getPrediction(@RequestParam String symbol) {
        return predictionService.getPrediction(symbol);
    }
}
