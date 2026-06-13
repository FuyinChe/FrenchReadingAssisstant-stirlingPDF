import { Container, Stack, Text, Title } from "@mantine/core";
import type { BaseToolProps } from "@app/types/tool";

/**
 * French Reader Tool — M0 skeleton.
 * M1+: PDF viewer + RegionSelector + AiSidePanel.
 */
export default function FrenchReader(_props: BaseToolProps) {
  return (
    <Container fluid py="md">
      <Stack gap="sm">
        <Title order={3}>French Reader</Title>
        <Text c="dimmed">
          Extension shell installed. PDF integration arrives in M1.
        </Text>
      </Stack>
    </Container>
  );
}
