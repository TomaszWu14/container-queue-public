import { defineFeature } from '../feature'

// Przegląd dostępów (US-076) i jego automat w katalogu Automatyzacji
export default defineFeature({
  pl: {
    accReviewTitle: 'Przegląd dostępów',
    accReviewIntro: 'Konta do decyzji: bez logowania od {days} dni (albo nigdy), admini bez 2FA i konta z dostępem do wszystkich spółek. Aktywnych kont: {active}. Raz na kwartał przypomnienie w dzwonku.',
    accReviewAllGood: 'Nic do sprawdzenia — wszystkie konta są używane i zabezpieczone.',
    accReviewColWhy: 'Dlaczego na liście', accReviewColLastSeen: 'Ostatnia aktywność', accReviewNever: 'nigdy',
    accReviewWhy_stale: 'Bez logowania od ponad 90 dni', accReviewWhy_never: 'Nigdy się nie zalogował',
    accReviewWhy_admin_no_2fa: 'Administrator bez 2FA', accReviewWhy_all_companies: 'Dostęp do wszystkich spółek',
    accReviewBlock: 'Zablokuj', accReviewConfirm: 'Zablokować konto {login}? Można je później odblokować na liście użytkowników.',
    autoName_access_review: 'Kwartalny przegląd dostępów', autoTrigger_access_review: 'Pierwszy poniedziałek kwartału, 8:00',
    autoAction_access_review: 'Dzwonek i mail do adminów: konta nieużywane, admini bez 2FA, dostęp do wszystkich spółek',
  },
  en: {
    accReviewTitle: 'Access review',
    accReviewIntro: 'Accounts to decide on: no sign-in for {days} days (or never), admins without 2FA and accounts with access to all companies. Active accounts: {active}. A reminder arrives once a quarter.',
    accReviewAllGood: 'Nothing to check — all accounts are in use and protected.',
    accReviewColWhy: 'Why listed', accReviewColLastSeen: 'Last activity', accReviewNever: 'never',
    accReviewWhy_stale: 'No sign-in for over 90 days', accReviewWhy_never: 'Never signed in',
    accReviewWhy_admin_no_2fa: 'Administrator without 2FA', accReviewWhy_all_companies: 'Access to all companies',
    accReviewBlock: 'Deactivate', accReviewConfirm: 'Deactivate account {login}? You can re-activate it later in the user list.',
    autoName_access_review: 'Quarterly access review', autoTrigger_access_review: 'First Monday of the quarter, 8:00',
    autoAction_access_review: 'Bell and email to admins: unused accounts, admins without 2FA, access to all companies',
  },
  pt: {
    accReviewTitle: 'Revisão de acessos',
    accReviewIntro: 'Contas a decidir: sem início de sessão há {days} dias (ou nunca), administradores sem 2FA e contas com acesso a todas as empresas. Contas ativas: {active}. Um lembrete chega uma vez por trimestre.',
    accReviewAllGood: 'Nada a verificar — todas as contas estão em uso e protegidas.',
    accReviewColWhy: 'Porque está na lista', accReviewColLastSeen: 'Última atividade', accReviewNever: 'nunca',
    accReviewWhy_stale: 'Sem início de sessão há mais de 90 dias', accReviewWhy_never: 'Nunca iniciou sessão',
    accReviewWhy_admin_no_2fa: 'Administrador sem 2FA', accReviewWhy_all_companies: 'Acesso a todas as empresas',
    accReviewBlock: 'Desativar', accReviewConfirm: 'Desativar a conta {login}? Pode reativá-la mais tarde na lista de utilizadores.',
    autoName_access_review: 'Revisão trimestral de acessos', autoTrigger_access_review: 'Primeira segunda-feira do trimestre, 8:00',
    autoAction_access_review: 'Sino e email para administradores: contas sem uso, administradores sem 2FA, acesso a todas as empresas',
  },
})
