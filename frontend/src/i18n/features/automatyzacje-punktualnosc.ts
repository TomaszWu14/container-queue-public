import { defineFeature } from '../feature'

// Punktualność armatorów i realne ETA (trzecia lista PO, pkt 7).
export default defineFeature({
  pl: {
    etaRelTitle: 'Punktualność armatorów i realne ETA',
    etaRelIntro: 'Spóźnienie = faktyczny wyładunek − pierwsze ETA, z ostatnich {d} dni; pokazujemy pary armator–port z co najmniej {n} przypłynięciami. Dodatnie dni = później niż obiecano.',
    etaRelEmpty: 'Za mało przypłynięć w historii, żeby ocenić punktualność.',
    etaRelCarrier: 'Armator', etaRelPort: 'Port', etaRelArrivals: 'Przypłynięcia', etaRelMedian: 'Mediana (dni)',
    etaRelP90: '90% przypłynięć do (dni)', etaRelLate: 'Spóźnione > 1 dzień',
    etaRelForecastTitle: 'Realne ETA kontenerów w drodze ({n})',
    etaRelForecast: '— ETA {eta}, realnie ok. {real} ({shift} dni wg historii {carrier})',
    etaRelBasis_carrier_port: 'armator i port, {n} przypłynięć', etaRelBasis_carrier: 'sam armator, {n} przypłynięć',
  },
  en: {
    etaRelTitle: 'Carrier punctuality and realistic ETA',
    etaRelIntro: 'Delay = actual discharge − first ETA, over the last {d} days; carrier–port pairs with at least {n} arrivals. Positive days = later than promised.',
    etaRelEmpty: 'Not enough arrivals in history to judge punctuality.',
    etaRelCarrier: 'Carrier', etaRelPort: 'Port', etaRelArrivals: 'Arrivals', etaRelMedian: 'Median (days)',
    etaRelP90: '90% of arrivals within (days)', etaRelLate: 'Late > 1 day',
    etaRelForecastTitle: 'Realistic ETA of containers in transit ({n})',
    etaRelForecast: '— ETA {eta}, realistically about {real} ({shift} days per {carrier} history)',
    etaRelBasis_carrier_port: 'carrier and port, {n} arrivals', etaRelBasis_carrier: 'carrier only, {n} arrivals',
  },
  pt: {
    etaRelTitle: 'Pontualidade dos armadores e ETA realista',
    etaRelIntro: 'Atraso = descarga real − primeiro ETA, nos últimos {d} dias; pares armador–porto com pelo menos {n} chegadas. Dias positivos = mais tarde do que o prometido.',
    etaRelEmpty: 'Chegadas insuficientes no histórico para avaliar a pontualidade.',
    etaRelCarrier: 'Armador', etaRelPort: 'Porto', etaRelArrivals: 'Chegadas', etaRelMedian: 'Mediana (dias)',
    etaRelP90: '90% das chegadas até (dias)', etaRelLate: 'Atrasadas > 1 dia',
    etaRelForecastTitle: 'ETA realista dos contentores em trânsito ({n})',
    etaRelForecast: '— ETA {eta}, realisticamente cerca de {real} ({shift} dias segundo o histórico de {carrier})',
    etaRelBasis_carrier_port: 'armador e porto, {n} chegadas', etaRelBasis_carrier: 'só armador, {n} chegadas',
  },
})
