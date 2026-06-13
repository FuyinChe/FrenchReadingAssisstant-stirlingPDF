import { ActionIcon, Loader, Tooltip } from "@mantine/core";
import { useTranslation } from "react-i18next";
import StopIcon from "@mui/icons-material/Stop";
import VolumeUpIcon from "@mui/icons-material/VolumeUp";

import { useFrenchReaderContext } from "@app/contexts/FrenchReaderContext";
import type { OcrLineResult } from "@app/hooks/tools/frenchReader/types";

interface TtsPlayButtonProps {
  text: string;
  lines: OcrLineResult[];
  size?: "sm" | "md";
}

export function TtsPlayButton({ text, lines, size = "md" }: TtsPlayButtonProps) {
  const { t } = useTranslation();
  const {
    playTts,
    stopTts,
    ttsBusy,
    ttsPlaying,
    ttsSynthesizing,
    ttsVoice,
  } = useFrenchReaderContext();

  const canPlay = Boolean(text.trim() && ttsVoice);
  const iconSize = size === "sm" ? 16 : 20;

  if (ttsBusy && (ttsPlaying || ttsSynthesizing)) {
    return (
      <Tooltip label={t("frenchReader.tts.stop", "Stop")}>
        <ActionIcon
          variant="light"
          color="red"
          size={size}
          onClick={(event) => {
            event.stopPropagation();
            stopTts();
          }}
          aria-label="Stop playback"
        >
          <StopIcon sx={{ fontSize: iconSize }} />
        </ActionIcon>
      </Tooltip>
    );
  }

  return (
    <Tooltip label={t("frenchReader.tts.play", "Read aloud")}>
      <ActionIcon
        variant="light"
        color="blue"
        size={size}
        disabled={!canPlay}
        loading={ttsSynthesizing}
        onClick={(event) => {
          event.stopPropagation();
          void playTts(text, lines);
        }}
        aria-label="Read aloud"
      >
        {ttsSynthesizing ? <Loader size="xs" /> : <VolumeUpIcon sx={{ fontSize: iconSize }} />}
      </ActionIcon>
    </Tooltip>
  );
}
