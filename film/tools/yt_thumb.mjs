// 上傳 YouTube 自訂縮圖：Studio 編輯頁找縮圖的 file input，選檔後按儲存。
import { open } from '/home/ct/ai-workshop-backend/scripts/lib/cdp.mjs'
const ID = 'VtVaP_HATBU', FILE = '/home/ct/larch-mimic-reborn/film/out/yt_thumb.jpg'
const sleep = ms => new Promise(r => setTimeout(r, ms))
const c = await open('studio.youtube', `https://studio.youtube.com/video/${ID}/edit`)
await sleep(15000)
const info = await c.ev(`JSON.stringify([...document.querySelectorAll('input[type=file]')].map(e=>({id:e.id,accept:e.accept,cls:e.className,parent:e.parentElement&&e.parentElement.tagName})))`)
console.log('file inputs', info)
const { root } = (await c.send('DOM.getDocument', { depth: -1, pierce: true })).result
const q = await c.send('DOM.querySelectorAll', { nodeId: root.nodeId, selector: 'input[type=file]' })
const ids = q.result?.nodeIds || []
let done = false
for (const nodeId of ids) {
  const a = (await c.send('DOM.getAttributes', { nodeId })).result?.attributes || []
  const acc = a[a.indexOf('accept') + 1] || ''
  if (/image/.test(acc)) { await c.send('DOM.setFileInputFiles', { nodeId, files: [FILE] }); done = true; console.log('選了縮圖檔，accept=', acc); break }
}
if (!done) { console.log('沒找到收圖片的 file input'); process.exit(1) }
await sleep(8000)
const hint = await c.ev(`(document.querySelector('ytcp-thumbnails-compact-editor-uploader, #still-picker, ytcp-video-thumbnail-editor')||document.body).innerText.slice(0,300)`)
console.log('縮圖區', hint)
await c.ev(`document.querySelector('#save').click()`)
await sleep(6000)
console.log('儲存後', (await c.ev(`(document.querySelector('#save')||{}).getAttribute ? document.querySelector('#save').getAttribute('disabled') : 'no-save'`)), (await c.ev(`document.body.innerText`)).match(/(已儲存變更|變更已儲存|Changes saved|無法[^\n]{0,30})/)?.[0] || '')
c.close(); process.exit(0)
