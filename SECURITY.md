# Política de segurança

## Escopo

Este é um projeto educacional de portfólio. Ele não deve receber dados pessoais reais. CPF, nome completo e data de nascimento são tratados como informações sensíveis mesmo em ambientes de demonstração.

## Relato de vulnerabilidades

Não publique detalhes exploráveis em uma issue aberta. Use um GitHub Security Advisory privado no repositório para descrever o impacto, os passos mínimos de reprodução e a versão afetada.

## Controles adotados

- autenticação e permissões de modelo;
- mascaramento e validação de CPF;
- proteção CSRF e cookies seguros;
- HTTPS, HSTS, CSP, SRI e headers restritivos;
- ausência de segredos e bancos no Git;
- PostgreSQL com TLS em produção;
- versões fixadas, Dependabot e auditoria de CVEs no CI.

## Limites

Antes de aceitar dados reais, implemente MFA, rate limiting distribuído, auditoria de ações, criptografia de campos, gestão de consentimento, retenção/expurgo, backup testado e revisão jurídica de privacidade aplicável.
