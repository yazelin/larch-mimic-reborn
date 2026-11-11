// 第二步：AI 合成內容選「是」、付費宣傳選「否」，等上傳與檢查完畢，設公開、按完成，回報影片網址。
import { open } from '/home/ct/ai-workshop-backend/scripts/lib/cdp.mjs'
const sleep = ms => new Promise(r => setTimeout(r, ms))
const c = await open('studio.youtube')
const ev = async (e, ms = 30000) => { for (let i = 0; i < 5; i++) { try { return await c.ev(e, ms) } catch { await sleep(4000) } } throw new Error('頁面沒有回應') }
await ev(`(async()=>{const s=ms=>new Promise(r=>setTimeout(r,ms))
  document.querySelector('[name=VIDEO_HAS_ALTERED_CONTENT_YES]').click(); await s(500)
  document.querySelector('[name=VIDEO_PAID_PRODUCT_PLACEMENT_NO]').click(); await s(500)})()`)
console.log('合成內容', await ev(`document.querySelector('[name=VIDEO_HAS_ALTERED_CONTENT_YES]').getAttribute('aria-checked')`),
            '兒童', await ev(`document.querySelector('[name=VIDEO_MADE_FOR_KIDS_NOT_MFK]').getAttribute('aria-checked')`))
let link = null
for (let i = 0; i < 240; i++) {                       // 最多等 40 分鐘
  const t = await ev(`(document.querySelector('ytcp-uploads-dialog')||document.body).innerText`).catch(() => '')
  link = (t.match(/https:\/\/youtu\.be\/([\w-]+)/) || [])[0] || link
  if (/每日.{0,6}上限|upload limit/i.test(t)) throw new Error('YouTube 每日上傳數量已達上限')
  if (t.includes('檢查完畢') && link) break
  if (i % 6 === 0) console.log('等待中', (t.match(/(上傳.{0,12}%|正在處理[^\n]{0,20}|檢查[^\n]{0,20})/) || [''])[0], link || '')
  await sleep(10000)
}
if (!link) throw new Error('沒有等到上傳完成')
await ev(`(async()=>{const s=ms=>new Promise(r=>setTimeout(r,ms))
  for(let i=0;i<3;i++){document.querySelector('#next-button').click(); await s(1800)}
  document.querySelector('[name=PUBLIC]').click(); await s(1000)})()`)
if (await ev(`document.querySelector('[name=PUBLIC]').getAttribute('aria-checked')`) !== 'true') throw new Error('沒有選到公開')
const btn = `document.querySelector('#done-button')`
for (let i = 0; i < 60 && await ev(`${btn}.hasAttribute('disabled') || ${btn}.getAttribute('aria-disabled') === 'true'`); i++) await sleep(5000)
await ev(`${btn}.click()`)
await sleep(6000)
console.log('完成後畫面', (await ev(`document.body.innerText`)).match(/(影片已發布|已發布|發布完成|Video published)[^\n]*/)?.[0] || '(沒看到發布字樣)')
console.log('LINK', link)
process.exit(0)
