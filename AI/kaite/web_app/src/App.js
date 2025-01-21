// src/App.jsx
import React, { useState, useRef } from "react";
import { Container, Button, Typography } from "@mui/material";
import { createTheme, ThemeProvider } from "@mui/material/styles";
import CssBaseline from "@mui/material/CssBaseline";

import AI from "./AI";

/**
 * parsePlaceholders:
 *   Replaces $1, $2, $3... with the result from chainResults[1], chainResults[2], etc.
 */
function parsePlaceholders(text, chainResults) {
  if (!text) return "";

  return text.replace(/\$([0-9]+)/g, (match, digitStr) => {
    const idx = parseInt(digitStr, 10);
    const res = chainResults[idx] || "";
    if (res) return res;
    return `(No result from AI #${idx})`;
  });
}

function App() {
  // For debugging, let's default to 3 AIs: #1, #2, #3
  const [aiList, setAiList] = useState([
    { id: 1 },
    { id: 2 },
    { id: 3 },
  ]);
  const [nextId, setNextId] = useState(4);

  // We'll store refs to each AI block (for calling executeDo)
  const aiRefs = useRef({});

  // MUI dark theme
  const darkTheme = createTheme({ palette: { mode: "dark" } });

  // Add a new AI
  const addAI = () => {
    setAiList((prev) => [...prev, { id: nextId }]);
    setNextId(nextId + 1);
  };

  // Remove an AI
  const removeAI = (id) => {
    setAiList((prev) => prev.filter((item) => item.id !== id));
  };

  /**
   * CHAIN ALL AIs (Parent-Managed Results)
   *
   * We'll keep a local array "chainResults",
   * where chainResults[i] = result from AI #i.
   * This avoids the timing problem of reading child state
   * before it updates in the same loop.
   */
  const chainAllAIs = async () => {
    console.log("=== Starting Chain All AIs (Parent-Managed) ===");

    // 1) We'll keep results in a simple object for easy indexing
    const chainResults = {};

    // 2) Iterate each AI in order
    for (let i = 0; i < aiList.length; i++) {
      const { id } = aiList[i];
      const ref = aiRefs.current[id];
      if (!ref) {
        console.log(`No ref for AI #${id}, skipping.`);
        continue;
      }

      console.log(`\n--- Processing AI #${id} ---`);

      // a) parse placeholders in that AI's typed text,
      //    referencing chainResults from *all* AIs so far
      //    (including the newly set ones as we proceed)
      const rawQuery = ref.getQuery();
      const rawPrompt = ref.getPrompt();

      // This is crucial: use chainResults (parent's data), not child states
      const finalQuery = parsePlaceholders(rawQuery, chainResults);
      const finalPrompt = parsePlaceholders(rawPrompt, chainResults);

      console.log(`AI #${id} raw query: "${rawQuery}"`);
      console.log(`AI #${id} raw prompt: "${rawPrompt}"`);
      console.log(`AI #${id} final query (parsed): "${finalQuery}"`);
      console.log(`AI #${id} final prompt (parsed): "${finalPrompt}"`);

      // b) call the child's do() with these replaced strings
      //    the child sets its own local state, but we also
      //    capture the result in chainResults so next AIs can use it
      const newResult = await ref.executeDo(finalQuery, finalPrompt);

      console.log(`AI #${id} => newResult: "${newResult}"`);

      // c) store in chainResults so that e.g. $1 or $2 can find it
      chainResults[id] = newResult || "";
    }

    console.log("=== Done Chaining All AIs ===");
    console.log("Final chainResults =>", chainResults);
  };

  return (
    <ThemeProvider theme={darkTheme}>
      <CssBaseline />
      <Container maxWidth="md" sx={{ py: 4 }}>
        <Typography variant="h4" gutterBottom>
          AI Chainer (Parent-Managed Results)
        </Typography>

        <Button variant="contained" onClick={addAI} sx={{ mr: 2, mb: 2 }}>
          Add AI
        </Button>
        <Button variant="outlined" onClick={chainAllAIs} sx={{ mb: 2 }}>
          Chain All AIs
        </Button>

        {aiList.map((item) => {
          const { id } = item;
          return (
            <AI
              key={id}
              aiId={id}
              onRemove={removeAI}
              ref={(el) => {
                aiRefs.current[id] = el;
              }}
            />
          );
        })}
      </Container>
    </ThemeProvider>
  );
}

export default App;
