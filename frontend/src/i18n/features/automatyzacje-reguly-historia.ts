import { defineFeature } from '../feature'

// Historia zmian reguł z kreatora (trzecia lista PO, pkt 4).
export default defineFeature({
  pl: {
    ruleHistTitle: 'Historia zmian reguł', ruleHistEmpty: 'Brak zmian.',
    ruleHist_added: 'dodano „{name}”', ruleHist_removed: 'usunięto „{name}”', ruleHist_changed: 'zmieniono „{name}”: {fields}',
    ruleHistRestore: 'Przywróć stan sprzed tej zmiany',
    ruleHistRestoreConfirm: 'Przywrócić regułę „{name}” do stanu sprzed tej zmiany? Pozostałe reguły zostaną bez zmian.',
    ruleHistField_name: 'nazwa', ruleHistField_enabled: 'włączenie', ruleHistField_condition: 'warunek',
    ruleHistField_days: 'dni', ruleHistField_status: 'etap', ruleHistField_notify: 'odbiorcy', ruleHistField_channels: 'kanały',
  },
  en: {
    ruleHistTitle: 'Rule change history', ruleHistEmpty: 'No changes.',
    ruleHist_added: 'added “{name}”', ruleHist_removed: 'removed “{name}”', ruleHist_changed: 'changed “{name}”: {fields}',
    ruleHistRestore: 'Restore the state before this change',
    ruleHistRestoreConfirm: 'Restore rule “{name}” to its state before this change? Other rules stay unchanged.',
    ruleHistField_name: 'name', ruleHistField_enabled: 'enabled', ruleHistField_condition: 'condition',
    ruleHistField_days: 'days', ruleHistField_status: 'stage', ruleHistField_notify: 'recipients', ruleHistField_channels: 'channels',
  },
  pt: {
    ruleHistTitle: 'Histórico de alterações das regras', ruleHistEmpty: 'Sem alterações.',
    ruleHist_added: 'adicionada «{name}»', ruleHist_removed: 'eliminada «{name}»', ruleHist_changed: 'alterada «{name}»: {fields}',
    ruleHistRestore: 'Repor o estado anterior a esta alteração',
    ruleHistRestoreConfirm: 'Repor a regra «{name}» no estado anterior a esta alteração? As outras regras ficam iguais.',
    ruleHistField_name: 'nome', ruleHistField_enabled: 'ativação', ruleHistField_condition: 'condição',
    ruleHistField_days: 'dias', ruleHistField_status: 'etapa', ruleHistField_notify: 'destinatários', ruleHistField_channels: 'canais',
  },
})
