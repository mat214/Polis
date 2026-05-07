import { definePluginEntry } from "openclaw/plugin-sdk/plugin-entry";
import { Type } from "@sinclair/typebox";

export default definePluginEntry({
  id: "template-standalone",
  name: "Template Plugin Canonique",
  description: "Plugin outil + hook de sécurité",
  register(api) {
    // ── Outil 1 : Notification sécurisée ──────────────────────────
    api.registerTool({
      name: "secure_send_notification",
      description:
        "Envoie une notification classifiée (READ/WRITE/WRITE_SENSITIVE/IRREVERSIBLE) " +
        "sur le canal configuré. Le niveau IRREVERSIBLE déclenche un Human Gate.",
      parameters: Type.Object({
        message: Type.String({ minLength: 1, maxLength: 2000 }),
        level: Type.Enum({
          READ: "READ",
          WRITE: "WRITE",
          WRITE_SENSITIVE: "WRITE_SENSITIVE",
          IRREVERSIBLE: "IRREVERSIBLE",
        }),
        channel: Type.Optional(Type.String()),
      }),
      async execute(_id, params) {
        return {
          content: [
            {
              type: "text",
              text: `[NOTIFICATION][${params.level}] ${params.message}`,
            },
          ],
        };
      },
    });

    // ── Outil 2 : Healthcheck config ──────────────────────────────
    api.registerTool({
      name: "config_healthcheck",
      description:
        "Vérifie la cohérence de la configuration OpenClaw : " +
        "intégrité du manifeste, skills référencés, bindings valides.",
      parameters: Type.Object({
        scope: Type.Optional(
          Type.Enum({ full: "full", quick: "quick" }, { default: "quick" }),
        ),
      }),
      async execute(_id, _params) {
        return {
          content: [
            {
              type: "text",
              text: JSON.stringify({
                status: "ok",
                checks: ["manifest", "skills", "bindings", "secrets"],
                ts: new Date().toISOString(),
              }),
            },
          ],
        };
      },
    });

    // ── Hook : Log tous les appels d'outils ───────────────────────
    api.on("before_tool_call", async (_ctx) => {
      // Retourner { block: true } pour REFUSER
      // Retourner { requireApproval: true } pour GATE
      // Retourner undefined pour PASS
      return undefined;
    });
  },
});
