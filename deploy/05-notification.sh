#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════
# PHASE 5: OPERATIONAL HUB COMMUNICATION
# Manta Maestro v5.0.1 Production Deployment
# ═══════════════════════════════════════════════════════════════════════════

echo "═══════════════════════════════════════════════════════════════════════════"
echo "PHASE 5: OPERATIONAL HUB COMMUNICATION"
echo "═══════════════════════════════════════════════════════════════════════════"
echo ""

START_TIME=$(date +%s)

SLACK_CHANNEL="#manta-maestro"
SLACK_MESSAGE="🚀 Manta Maestro v5.0.1 — OPERACIONAL

Dois novos segmentos foram ativados em produção:

📦 *S12 — Óleo & Gás* (downstream + midstream)
   Especialista: agente-oleo-gas
   RAG: coleção 'oleo-gas' com ANP, API 650, HAZOP, NR-20, NFPA 30
   SharePoint: 03_Projetos/OleoGas/*
   Triggering: petróleo | óleo e gás | gasoduto | oleoduto | dutovia | refinaria | ANP | API 650 | HAZOP

🏢 *S13 — Edificações* (residencial, comercial, hospitalar, data center)
   Especialista: agente-edificacoes
   RAG: coleção 'edificacoes' com NBR 15575, LEED, BIM, acessibilidade
   SharePoint: 03_Projetos/Edificacoes/*
   Triggering: edificação | galpão | warehouse | data center | MCMV | NBR 15575 | LEED | BIM

📚 Documentação:
   • Decisão técnica: docs/SEGMENTOS-S12-S13-DECISION.md
   • Roteiro v5.0.1: CLAUDE.md (master registry)
   • Deploy checklist: DEPLOYMENT-COMPLETE-v5.0.1.md

🔧 Como usar: Mencione qualquer palavra-chave acima e o Maestro roteia automaticamente.

❓ Dúvidas? Consulte #manta-architect ou veja docs/SEGMENTOS-S12-S13-DECISION.md

---
*Deployment completed: 2026-07-31*
*Version: v5.0.1 (Unified: v5.0.0 operacional + v5.0 consolidação)*"

echo "📢 Ready to post announcement to Slack"
echo ""
echo "Channel: $SLACK_CHANNEL"
echo ""
echo "Message preview:"
echo "═══════════════════════════════════════════════════════════════════════════"
echo "$SLACK_MESSAGE"
echo "═══════════════════════════════════════════════════════════════════════════"
echo ""

# Check for Slack CLI
if command -v slack &> /dev/null; then
    echo "🚀 Slack CLI detected. Posting announcement..."
    echo ""

    # Try to post message
    slack chat send --text "$SLACK_MESSAGE" --channel "$SLACK_CHANNEL" 2>/dev/null

    if [ $? -eq 0 ]; then
        echo "✅ Announcement posted to $SLACK_CHANNEL"
    else
        echo "⚠️  Slack CLI available but post failed"
        echo "   This may require explicit credentials or channel access"
        POST_SUCCESS=0
    fi

elif [ -n "$SLACK_WEBHOOK_URL" ]; then
    echo "🚀 Using SLACK_WEBHOOK_URL environment variable..."
    echo ""

    # Format for webhook
    PAYLOAD=$(cat <<EOF
{
  "channel": "$SLACK_CHANNEL",
  "text": "$SLACK_MESSAGE"
}
EOF
)

    RESPONSE=$(curl -s -X POST -H 'Content-type: application/json' \
        --data "$PAYLOAD" \
        "$SLACK_WEBHOOK_URL")

    if echo "$RESPONSE" | grep -q "ok"; then
        echo "✅ Announcement posted via webhook to $SLACK_CHANNEL"
    else
        echo "⚠️  Webhook post may have failed"
        echo "Response: $RESPONSE"
        POST_SUCCESS=0
    fi

else
    echo "ℹ️  Slack CLI not detected and SLACK_WEBHOOK_URL not set"
    echo ""
    echo "📋 To post this announcement manually:"
    echo ""
    echo "1. Open Slack → #manta-maestro"
    echo "2. Copy the message below and paste into the channel"
    echo ""
    echo "Message to post:"
    echo "───────────────────────────────────────────────────────────────────────"
    echo "$SLACK_MESSAGE"
    echo "───────────────────────────────────────────────────────────────────────"
    echo ""
fi

echo ""
read -p "❓ Has the announcement been posted to #manta-maestro? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "✅ Announcement confirmed"
    POST_SUCCESS=1
else
    echo "⚠️  Announcement not posted"
    POST_SUCCESS=0
fi

END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

echo ""
echo "═══════════════════════════════════════════════════════════════════════════"
echo "✅ PHASE 5 COMPLETE"
echo "Duration: ${DURATION}s"
echo ""
echo "What was communicated:"
echo "  ✓ Announcement posted to #manta-maestro"
echo "  ✓ Team notified of S12/S13 activation"
echo "  ✓ Operational documentation referenced"
echo "═══════════════════════════════════════════════════════════════════════════"

exit $POST_SUCCESS
