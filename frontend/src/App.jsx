import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { Sparkles, Wand2 } from "lucide-react";
import {
  checkApiHealth,
  clearHistory,
  deleteHistoryItem,
  generateImage,
  generatePrompt,
  getHistory,
  saveHistory,
  uploadReference,
} from "./api";
import "./App.css";

const moods = ["Mysterious", "Friendly", "Epic", "Dark", "Cute", "Futuristic", "Magical"];

const artStyles = [
  "Fantasy RPG",
  "Cyberpunk",
  "Anime",
  "Pixel Art",
  "Dark Fantasy",
  "Sci-Fi",
  "3D Game Concept Art",
  "Soft Aesthetic",
  "Ethereal Fantasy",
  "Pastel Moodboard",
  "Cinematic Concept Art",
  "Dark Academia Fantasy",
  "Cozy Magical",
  "Y2K Cyber Fantasy",
];

const environments = [
  "Mystic Forest",
  "Neon City",
  "Ancient Castle",
  "Space Station",
  "Desert Ruins",
  "Underwater Kingdom",
  "Battle Arena",
  "Dreamy Cloud Realm",
  "Vintage Library",
  "Moonlit Lake",
  "Cozy Witch Cottage",
  "Floating Island",
  "Glowing Flower Garden",
  "Rainy Neon Street",
  "Crystal Cave",
];

function getDragonTheme(artStyle, companionMood, environment) {
  if (artStyle.includes("Cyberpunk") || environment.includes("Neon")) {
    return {
      primary: "#6ee7ff",
      secondary: "#ff4fd8",
      accent: "#faff72",
      aura: "rgba(110, 231, 255, 0.30)",
    };
  }

  if (artStyle.includes("Dark")) {
    return {
      primary: "#d8d4ff",
      secondary: "#7f1dff",
      accent: "#ff4d6d",
      aura: "rgba(127, 29, 255, 0.28)",
    };
  }

  if (artStyle.includes("Soft") || artStyle.includes("Pastel") || artStyle.includes("Cozy")) {
    return {
      primary: "#ffe4f3",
      secondary: "#a7f3d0",
      accent: "#fef3c7",
      aura: "rgba(255, 228, 243, 0.30)",
    };
  }

  if (artStyle.includes("Sci-Fi") || environment.includes("Space")) {
    return {
      primary: "#dff8ff",
      secondary: "#38bdf8",
      accent: "#c4b5fd",
      aura: "rgba(56, 189, 248, 0.28)",
    };
  }

  if (companionMood === "Cute") {
    return {
      primary: "#ffd6e8",
      secondary: "#b8f7d4",
      accent: "#fff1a8",
      aura: "rgba(255, 214, 232, 0.30)",
    };
  }

  if (companionMood === "Epic") {
    return {
      primary: "#fff1b8",
      secondary: "#34d399",
      accent: "#f59e0b",
      aura: "rgba(245, 158, 11, 0.28)",
    };
  }

  return {
    primary: "#d8fff6",
    secondary: "#6d5cff",
    accent: "#ffe6a8",
    aura: "rgba(86, 255, 210, 0.22)",
  };
}

function DragonCompanion({ artStyle, companionMood, environment }) {
  const theme = getDragonTheme(artStyle, companionMood, environment);

  return (
    <motion.div
      className="dragon-wrap"
      style={{
        "--dragon-primary": theme.primary,
        "--dragon-secondary": theme.secondary,
        "--dragon-accent": theme.accent,
        "--dragon-aura": theme.aura,
      }}
      initial={{ x: -420, y: 260, rotate: -16, opacity: 0 }}
      animate={{ x: 0, y: 0, rotate: 0, opacity: 1 }}
      transition={{ duration: 1.4, ease: "easeOut" }}
    >
      <div className="dragon-aura" />
      <div className="dragon-trail trail-one" />
      <div className="dragon-trail trail-two" />

      <motion.div
        className="dragon-body"
        animate={{ y: [0, -10, 0], rotate: [0, 1.5, 0] }}
        transition={{ duration: 4, repeat: Infinity, ease: "easeInOut" }}
      >
        <div className="dragon-tail" />
        <div className="dragon-curve curve-one" />
        <div className="dragon-curve curve-two" />
        <div className="dragon-neck" />
        <div className="dragon-spines">
          <span />
          <span />
          <span />
          <span />
          <span />
        </div>
        <div className="dragon-scales">
          <span />
          <span />
          <span />
          <span />
          <span />
          <span />
        </div>
        <div className="dragon-head">
          <span className="horn horn-left" />
          <span className="horn horn-right" />
          <span className="eye eye-left" />
          <span className="eye eye-right" />
          <span className="whisker whisker-left" />
          <span className="whisker whisker-right" />
        </div>
      </motion.div>
    </motion.div>
  );
}

function App() {
  const [setupComplete, setSetupComplete] = useState(false);
  const [companionMood, setCompanionMood] = useState("Mysterious");
  const [artStyle, setArtStyle] = useState("Fantasy RPG");
  const [environment, setEnvironment] = useState("Mystic Forest");

  const [activeView, setActiveView] = useState("studio");
  const [historyItems, setHistoryItems] = useState([]);
  const [librarySearch, setLibrarySearch] = useState("");
  const [libraryStatusFilter, setLibraryStatusFilter] = useState("All");
  const [libraryMessage, setLibraryMessage] = useState("");
  const [apiOnline, setApiOnline] = useState(false);
  const [characterPrompt, setCharacterPrompt] = useState("");
  const [enhancement, setEnhancement] = useState("Balanced");
  const [referenceFile, setReferenceFile] = useState(null);
  const [referenceInstruction, setReferenceInstruction] = useState("No reference image provided.");
  const [finalPrompt, setFinalPrompt] = useState("");
  const [characterSummary, setCharacterSummary] = useState("");
  const [imageStatus, setImageStatus] = useState("idle");
  const [generatedImagePath, setGeneratedImagePath] = useState("");
  const [generateImageNow, setGenerateImageNow] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");

  useEffect(() => {
    async function checkStatus() {
      try {
        await checkApiHealth();
        setApiOnline(true);
      } catch {
        setApiOnline(false);
      }
    }

    checkStatus();
  }, []);

  async function handleGenerateCharacter() {
    if (!characterPrompt.trim()) {
      setErrorMessage("Please describe your character first.");
      return;
    }

    setIsGenerating(true);
    setErrorMessage("");
    setImageStatus("idle");
    setGeneratedImagePath("");

    try {
      const promptResponse = await generatePrompt({
        character_prompt: characterPrompt,
        companion_mood: companionMood,
        art_style: artStyle,
        environment,
        enhancement,
        reference_instruction: referenceInstruction,
      });

      const newFinalPrompt = promptResponse.final_prompt;
      setFinalPrompt(newFinalPrompt);

      const referenceImagePath = await uploadReference(referenceFile);

      let generatedPath = null;
      let currentImageStatus = "skipped";

      if (generateImageNow) {
        const imageResponse = await generateImage(newFinalPrompt);
        currentImageStatus = imageResponse.status;

        if (imageResponse.status === "success") {
          generatedPath = imageResponse.generated_image_path;
          setGeneratedImagePath(generatedPath);
        }
      }

      setImageStatus(currentImageStatus);

      await saveHistory({
        character_prompt: characterPrompt,
        art_style: artStyle,
        environment,
        enhancement,
        reference_instruction: referenceInstruction,
        reference_image_path: referenceImagePath,
        generated_image_path: generatedPath,
        image_status: currentImageStatus,
        final_prompt: newFinalPrompt,
      });

      setCharacterSummary(`Style: ${artStyle}
Environment: ${environment}
Creative direction: ${enhancement}

Core idea:
${characterPrompt}`);
    } catch (error) {
      setErrorMessage(error.message || "Something went wrong.");
    } finally {
      setIsGenerating(false);
    }
  }

  async function loadHistoryItems() {
    try {
      const items = await getHistory();
      setHistoryItems(items);
      setLibraryMessage("");
    } catch (error) {
      setLibraryMessage(error.message || "Could not load concept history.");
    }
  }

  async function handleDeleteHistoryItem(historyId) {
    try {
      await deleteHistoryItem(historyId);
      await loadHistoryItems();
    } catch (error) {
      setLibraryMessage(error.message || "Could not delete concept.");
    }
  }

  async function handleClearHistory() {
    try {
      await clearHistory();
      await loadHistoryItems();
    } catch (error) {
      setLibraryMessage(error.message || "Could not clear history.");
    }
  }

  const filteredHistoryItems = historyItems.filter((item) => {
    const query = librarySearch.toLowerCase();

    const matchesSearch =
      item.character_prompt?.toLowerCase().includes(query) ||
      item.art_style?.toLowerCase().includes(query) ||
      item.environment?.toLowerCase().includes(query);

    const matchesStatus =
      libraryStatusFilter === "All" || item.image_status === libraryStatusFilter;

    return matchesSearch && matchesStatus;
  });

  if (!setupComplete) {
    return (
      <main className="intro-page">
        <div className="mist mist-one" />
        <div className="mist mist-two" />

        <section className="intro-shell">
          <div className="intro-copy">
            <p className="eyebrow">AI Creative Companion</p>
            <h1>The dragon has arrived to shape your world.</h1>
            <p className="intro-text">
              Choose the mood, art direction, and environment for your creative guide before
              building your game character.
            </p>

            <div className="setup-panel">
              <label>
                Companion mood
                <select value={companionMood} onChange={(event) => setCompanionMood(event.target.value)}>
                  {moods.map((mood) => (
                    <option key={mood}>{mood}</option>
                  ))}
                </select>
              </label>

              <label>
                Art style
                <select value={artStyle} onChange={(event) => setArtStyle(event.target.value)}>
                  {artStyles.map((style) => (
                    <option key={style}>{style}</option>
                  ))}
                </select>
              </label>

              <label>
                Environment
                <select value={environment} onChange={(event) => setEnvironment(event.target.value)}>
                  {environments.map((world) => (
                    <option key={world}>{world}</option>
                  ))}
                </select>
              </label>

              <button className="primary-button" onClick={() => setSetupComplete(true)}>
                <Wand2 size={18} />
                Start Creating
              </button>
            </div>
          </div>

          <div className="dragon-stage">
            <DragonCompanion
              artStyle={artStyle}
              companionMood={companionMood}
              environment={environment}
            />
            <div className="dragon-message">
              <Sparkles size={18} />
              <span>
                {companionMood} guide entering a {environment} in {artStyle} style.
              </span>
            </div>
          </div>
        </section>
      </main>
    );
  }

  return (
    <main className="studio-page">
      <nav className="topbar">
        <div>
          <p className="eyebrow">AI Game Character Generator</p>
          <h2>Character Studio</h2>
        </div>

        <div className="nav-actions">
          <span className={`status-pill ${apiOnline ? "online" : "offline"}`}>
            {apiOnline ? "API connected" : "API offline"}
          </span>
          <button className="ghost-button" onClick={() => setActiveView("studio")}>
            Studio
          </button>
          <button
            className="ghost-button"
            onClick={() => {
              setActiveView("library");
              loadHistoryItems();
            }}
          >
            Concept Library
          </button>
          <button className="ghost-button" onClick={() => setSetupComplete(false)}>
            Change Companion
          </button>
        </div>
      </nav>

      {activeView === "studio" ? (
        <>
          <section className="studio-hero">
            <div>
              <h1>Create your next game character.</h1>
              <p>
                Companion mood: {companionMood} · Art style: {artStyle} · Environment:{" "}
                {environment}
              </p>
            </div>

            <DragonCompanion
              artStyle={artStyle}
              companionMood={companionMood}
              environment={environment}
            />
          </section>

          <section className="studio-grid">
            <div className="studio-panel">
              <div className="panel-heading">
                <p className="eyebrow">Character Brief</p>
                <h3>Describe the character you want to create.</h3>
              </div>

              <label>
                Character idea
                <textarea
                  value={characterPrompt}
                  onChange={(event) => setCharacterPrompt(event.target.value)}
                  placeholder="Example: A mysterious king with moonlit armor, ancient magic, and a hidden curse"
                />
              </label>

              <label>
                Creative direction
                <select value={enhancement} onChange={(event) => setEnhancement(event.target.value)}>
                  {[
                    "Balanced",
                    "More cinematic",
                    "More mysterious",
                    "More cute",
                    "More powerful",
                    "More realistic",
                    "More magical",
                  ].map((option) => (
                    <option key={option}>{option}</option>
                  ))}
                </select>
              </label>

              <label>
                Upload visual reference optional
                <input
                  type="file"
                  accept="image/png,image/jpeg"
                  onChange={(event) => setReferenceFile(event.target.files[0] || null)}
                />
              </label>

              {referenceFile && (
                <div className="reference-preview">
                  <img src={URL.createObjectURL(referenceFile)} alt="Reference preview" />
                  <div>
                    <strong>{referenceFile.name}</strong>
                    <span>{Math.round(referenceFile.size / 1024)} KB</span>
                  </div>
                </div>
              )}

              <label>
                Reference guidance
                <textarea
                  value={referenceInstruction}
                  onChange={(event) => setReferenceInstruction(event.target.value)}
                  placeholder="Example: Use the glowing blue mood and soft magical lighting from this image, but create a completely new character."
                />
              </label>

              <label className="check-row">
                <input
                  type="checkbox"
                  checked={generateImageNow}
                  onChange={(event) => setGenerateImageNow(event.target.checked)}
                />
                Generate image now
              </label>

              {errorMessage && <p className="error-text">{errorMessage}</p>}

              <button className="primary-button" onClick={handleGenerateCharacter} disabled={isGenerating}>
                <Wand2 size={18} />
                {isGenerating ? "Generating..." : "Generate Character"}
              </button>
            </div>

            <div className="studio-panel result-panel">
              <div className="panel-heading">
                <p className="eyebrow">Result</p>
                <h3>Character output</h3>
              </div>

              {imageStatus === "success" && generatedImagePath ? (
                <div className="image-result">
                  <p>Generated image saved:</p>
                  <code>{generatedImagePath}</code>
                </div>
              ) : (
                <div className="empty-result">
                  <Sparkles size={24} />
                  <p>
                    {imageStatus === "skipped"
                      ? "Image generation skipped. Prompt and concept were saved."
                      : "Your generated character result will appear here."}
                  </p>
                </div>
              )}

              {characterSummary && (
                <div className="summary-box">
                  <h4>Character Summary</h4>
                  <pre>{characterSummary}</pre>
                </div>
              )}

              {finalPrompt && (
                <details className="prompt-preview" open>
                  <summary>Prompt Preview</summary>
                  <pre>{finalPrompt}</pre>
                </details>
              )}
            </div>
          </section>
        </>
      ) : (
        <section className="library-page">
          <div className="library-header">
            <div>
              <p className="eyebrow">Concept Library</p>
              <h1>Saved character concepts.</h1>
            </div>
            <button className="ghost-button" onClick={handleClearHistory}>
              Clear Library
            </button>
          </div>

          <div className="library-controls">
            <input
              type="text"
              value={librarySearch}
              onChange={(event) => setLibrarySearch(event.target.value)}
              placeholder="Search by character, style, or environment"
            />

            <select
              value={libraryStatusFilter}
              onChange={(event) => setLibraryStatusFilter(event.target.value)}
            >
              <option>All</option>
              <option>skipped</option>
              <option>success</option>
              <option>error</option>
            </select>
          </div>

          {libraryMessage && <p className="error-text">{libraryMessage}</p>}

          {filteredHistoryItems.length === 0 ? (
            <div className="empty-result">
              <Sparkles size={24} />
              <p>No saved concepts found.</p>
            </div>
          ) : (
            <div className="concept-grid">
              {filteredHistoryItems.map((item) => (
                <article className="concept-card" key={item.id}>
                  <div className="concept-card-header">
                    <span>{item.art_style}</span>
                    <span>{item.image_status || "unknown"}</span>
                  </div>

                  <h3>{item.character_prompt}</h3>
                  <p>{item.environment}</p>

                  <div className="concept-meta">
                    {item.created_at && <span>Created: {item.created_at}</span>}
                    {item.enhancement && <span>Direction: {item.enhancement}</span>}
                    {item.reference_image_path && <span>Reference: {item.reference_image_path}</span>}
                    {item.generated_image_path && <span>Generated: {item.generated_image_path}</span>}
                  </div>

                  {item.reference_instruction && (
                    <details>
                      <summary>Reference guidance</summary>
                      <pre>{item.reference_instruction}</pre>
                    </details>
                  )}

                  <details>
                    <summary>View prompt</summary>
                    <pre>{item.final_prompt}</pre>
                  </details>

                  <button className="ghost-button" onClick={() => handleDeleteHistoryItem(item.id)}>
                    Delete
                  </button>
                </article>
              ))}
            </div>
          )}
        </section>
      )}
    </main>
  );
}

export default App;