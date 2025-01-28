// src/AI.jsx
import React, {
    useState,
    forwardRef,
    useImperativeHandle
} from "react";
import axios from "axios";
import {
    Box,
    Button,
    IconButton,
    Paper,
    Stack,
    TextField,
    Typography,
    Collapse
} from "@mui/material";
import RemoveCircleOutlineIcon from "@mui/icons-material/RemoveCircleOutline";

const AI = forwardRef((props, ref) => {
    const { onRemove, aiId } = props;

    const [expanded, setExpanded] = useState(true);

    const [fileName, setFileName] = useState("");
    const [name, setName] = useState("");

    // For the prompt inside Character
    const [core, setCore] = useState("");
    const [flux, setFlux] = useState("");
    const [memories, setMemories] = useState("");

    const [query, setQuery] = useState("");
    const [result, setResult] = useState("");

    const [message, setMessage] = useState("");

    const JSON_API_URL = "http://localhost:8000";
    const AI_API_URL = "http://localhost:3001";

    // Load JSON
    const handleLoadData = async () => {
        if (!fileName) {
            setMessage("Please enter a filename to load.");
            return;
        }
        try {
            const response = await axios.get(`${JSON_API_URL}/read-json/${fileName}`);
            const data = response.data;

            // Existing fields
            setName(data.name || "");

            if (data.prompt) {
                setCore(data.prompt.core || "");
                setFlux(data.prompt.flux || "");
                setMemories(data.prompt.memories || "");
            } else {
                setCore("");
                setFlux("");
                setMemories("");
            }

            setMessage(`Loaded data from ${fileName}.json successfully.`);
        } catch (error) {
            if (error.response && error.response.status === 404) {
                setMessage(`File "${fileName}.json" not found.`);
            } else {
                setMessage("Error loading file. Check console for details.");
                console.error(error);
            }
        }
    };

    // Save JSON
    const handleSaveData = async () => {
        if (!fileName) {
            setMessage("Please enter a filename to save.");
            return;
        }
        try {
            // Build the nested structure to match the Pydantic model
            const requestBody = {
                name,
                prompt: {
                    core,
                    flux,
                    memories
                },
            };

            await axios.post(`${JSON_API_URL}/write-json/${fileName}`, requestBody);

            setMessage(`Saved data to ${fileName}.json successfully.`);
        } catch (error) {
            setMessage("Error saving file. Check console for details.");
            console.error(error);
        }
    };

    // do() endpoint
    const handleExecuteDo = async (forcedQuery = null, forcedPrompt = null) => {
        try {
            setResult("");
            setMessage("");

            const q = forcedQuery !== null ? forcedQuery : query;
            const p = forcedPrompt !== null ? forcedPrompt : prompt;

            console.log(
                `AI #${aiId} handleExecuteDo() -> sending query="${q}" prompt="${p}"`
            );

            if (!q || !p) {
                setMessage("Please enter both query and prompt to submit.");
                return;
            }

            const response = await axios.post(`${AI_API_URL}/do`, {
                query: q,
                prompt: p,
            });

            const doResult = response.data.result;
            console.log(`AI #${aiId} handleExecuteDo() -> got result="${doResult}"`);

            setResult(doResult);
            setMessage("Executed do() successfully.");
            return doResult;
        } catch (err) {
            setMessage("Error calling do() API. Check console for details.");
            console.error(err);
            throw err;
        }
    };

    useImperativeHandle(ref, () => ({
        async executeDo(q = null, p = null) {
            return await handleExecuteDo(q, p);
        },
        setQuery: (val) => setQuery(val),
        getResult: () => result,
        getQuery: () => query,
    }));

    const handleToggleExpand = () => {
        setExpanded((prev) => !prev);
    };

    return (
        <Paper elevation={3} sx={{ mb: 2, position: "relative" }}>
            <Box
                sx={{
                    display: "flex",
                    alignItems: "center",
                    p: 2,
                    cursor: "pointer",
                }}
                onClick={handleToggleExpand}
            >
                <Typography variant="h6" sx={{ flexGrow: 1 }}>
                    AI Block {aiId} - {name}
                </Typography>
                <IconButton
                    color="error"
                    onClick={(e) => {
                        e.stopPropagation();
                        onRemove(aiId);
                    }}
                    title="Remove this AI"
                >
                    <RemoveCircleOutlineIcon />
                </IconButton>
            </Box>

            <Collapse in={expanded}>
                <Box sx={{ p: 2 }}>
                    <Box sx={{ mb: 3 }}>
                        <TextField
                            label="Filename (without .json)"
                            variant="outlined"
                            fullWidth
                            value={fileName}
                            onChange={(e) => setFileName(e.target.value)}
                            sx={{ mb: 2 }}
                        />
                        <Stack direction="row" spacing={2} sx={{ mb: 2 }}>
                            <Button variant="contained" onClick={handleLoadData}>
                                Load JSON
                            </Button>
                            <Button variant="contained" color="secondary" onClick={handleSaveData}>
                                Save JSON
                            </Button>
                        </Stack>

                        <Box sx={{ mt: 2 }}>
                            <TextField
                                label="Name"
                                variant="outlined"
                                fullWidth
                                value={name}
                                onChange={(e) => setName(e.target.value)}
                            /></Box>

                        <Box sx={{ mt: 2 }}>
                            <TextField
                                label="Prompt Core"
                                variant="outlined"
                                fullWidth
                                value={core}
                                onChange={(e) => setCore(e.target.value)}
                            /></Box>

                        <Box sx={{ mt: 2 }}>
                            <TextField
                                label="Prompt Flux"
                                variant="outlined"
                                fullWidth
                                value={flux}
                                onChange={(e) => setFlux(e.target.value)}
                            /></Box>

                        <Box sx={{ mt: 2 }}>
                            <TextField
                                label="Prompt Memories"
                                variant="outlined"
                                fullWidth
                                value={memories}
                                onChange={(e) => setMemories(e.target.value)}
                            /></Box>
                    </Box>

                    <Box sx={{ mb: 2 }}>
                        <TextField
                            label="Query"
                            variant="outlined"
                            fullWidth
                            sx={{ mb: 2 }}
                            value={query}
                            onChange={(e) => setQuery(e.target.value)}
                        />
                        {/* Normal "Submit" just calls do() with typed text, no placeholders */}
                        <Button variant="contained" onClick={() => handleExecuteDo()}>
                            Submit
                        </Button>
                    </Box>

                    <TextField
                        label="Result"
                        multiline
                        rows={5}
                        fullWidth
                        value={result}
                        onChange={() => { }}
                    />

                    {message && (
                        <Typography variant="body2" color="primary" sx={{ mt: 1 }}>
                            {message}
                        </Typography>
                    )}
                </Box>
            </Collapse>
        </Paper>
    );
});

export default AI;
