import { Router } from "express";

const router = Router();

// --- Agent orchestration routes ---

/**
 * Orchestrates a multi-step agent workflow.
 */
router.post("/orchestrate", async (req, res) => {
  try {
    const { task, steps } = req.body;
    if (!task || !steps) {
      return res.status(400).json({ error: "Missing required fields" });
    }

    // Step 1: Research
    const researchResult = await agentService.research(task);
    console.log("Research complete:", researchResult.summary?.length, "sources");

    // Step 2: Analyze (if sources found)
    let analysisResult;
    if (researchResult.sources.length > 0) {
      analysisResult = await agentService.analyze(researchResult.sources);
      console.log("Analysis complete:", analysisResult.summary?.length, "insights");
    } else {
      analysisResult = null;
    }

    // Step 3: Synthesize
    const synthesisResult = await agentService.synthesize(
      researchResult,
      analysisResult || {}
    );
    console.log("Synthesis complete:", synthesisResult.summary?.length, "words");

    return res.json({
      success: true,
      data: {
        summary: synthesisResult.summary,
        sources: synthesisResult.sources,
        confidence: synthesisResult.confidence,
        stepsCompleted: 3,
      },
    });
  } catch (error) {
    console.error("Orchestration error:", error);
    return res.status(500).json({ error: "Agent orchestration failed" });
  }
});

export default router;
