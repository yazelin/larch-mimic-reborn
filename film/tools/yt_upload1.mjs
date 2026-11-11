// 第一步：開上傳、選檔、填標題簡介、選「不是兒童專屬」，列出詳細資料頁的選項名稱（不按下一步）。
// 沿用 ~/ai-workshop-backend/scripts/yt-upload.mjs 的 CDP 做法（9333 已登入 Chrome）。
import { readFileSync } from 'node:fs'
import { open } from '/home/ct/ai-workshop-backend/scripts/lib/cdp.mjs'
const CHANNEL = 'UCOfFvRR1-TtYlok8FrwuE0A'
const FILE = '/home/ct/larch-mimic-reborn/film/out/轉生成寶箱怪的我_1080p.mp4'
const TITLE = '轉生成寶箱怪的我｜完整故事'
const DESC = readFileSync('/home/ct/larch-mimic-reborn/film/yt_description.txt', 'utf8').trim()
const sleep = ms => new Promise(r => setTimeout(r, ms))
const c = await open('studio.youtube', `https://studio.youtube.com/channel/${CHANNEL}/videos/upload`)
await sleep(12000)
await c.ev(`(async()=>{(document.querySelector('#create-icon')||document.querySelector('button[aria-label=建立]')).click(); await new Promise(r=>setTimeout(r,1000)); document.querySelector('#text-item-0').click()})()`)
await sleep(3000)
const { root } = (await c.send('DOM.getDocument', { depth: -1, pierce: true })).result
const { nodeId } = (await c.send('DOM.querySelector', { nodeId: root.nodeId, selector: 'input[type=file]' })).result
await c.send('DOM.setFileInputFiles', { nodeId, files: [FILE] })
await sleep(15000)
console.log('對話框', await c.ev(`!!document.querySelector('ytcp-uploads-dialog')`))
await c.ev(`(async()=>{
  const s=ms=>new Promise(r=>setTimeout(r,ms))
  const set=(sel,text)=>{const e=document.querySelector(sel); e.focus(); document.execCommand('selectAll'); document.execCommand('insertText',false,text)}
  set('ytcp-social-suggestions-textbox#title-textarea #textbox', ${JSON.stringify(TITLE)})
  set('ytcp-social-suggestions-textbox#description-textarea #textbox', ${JSON.stringify(DESC)})
  await s(800)
  document.querySelector('[name=VIDEO_MADE_FOR_KIDS_NOT_MFK]').click()
  await s(800)
  const more=[...document.querySelectorAll('ytcp-button, button')].find(b=>/顯示更多|Show more/.test(b.innerText)); if(more) more.click()
  await s(1500)
})()`)
const names = await c.ev(`JSON.stringify([...document.querySelectorAll('ytcp-uploads-dialog [name]')].map(e=>e.getAttribute('name')+' | '+(e.innerText||'').trim().slice(0,40)+' | '+e.getAttribute('aria-checked')))`)
console.log(JSON.parse(names).join('\n'))
const alt = await c.ev(`(()=>{const t=document.querySelector('ytcp-uploads-dialog').innerText; const i=t.search(/變造|合成|Altered/); return i<0?'沒找到':t.slice(i-60,i+300)})()`)
console.log('--- 合成內容段落 ---\n' + alt)
console.log('標題', await c.ev(`document.querySelector('ytcp-social-suggestions-textbox#title-textarea #textbox').innerText`))
process.exit(0)
