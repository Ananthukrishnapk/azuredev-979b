import { createUnlighthouse } from '@unlighthouse/core'
import { writeFile } from 'node:fs/promises'
import { join } from 'path'
import { fileURLToPath } from 'url'
import path from 'path'
import fs from "fs"
import { ensureDir } from './utils.js'
import whyIsNodeRunning from 'why-is-node-running'

const __filename = fileURLToPath(import.meta.url)
const src_folder = path.dirname(__filename)
const scripts_folder = src_folder + '/' + '../'
const project_dir = scripts_folder + '../'
const root_dir = project_dir + '../'
const CONFIG_PATH = root_dir + 'config.yml'

import YAML from "yaml"
import { getConfig, AppConfigSchema } from "./config.js"
const config_raw = YAML.parse(fs.readFileSync(CONFIG_PATH, "utf8"))

const CONFIG_VALIDATED = AppConfigSchema.parse(config_raw)
const CONFIG = getConfig(CONFIG_VALIDATED, project_dir)

ensureDir(CONFIG.temp_dir)
ensureDir(CONFIG.unligthouse_reports_dir)

console.log(CONFIG);


async function runUnlighthouse(site_url, runId?: string) {
  return new Promise(async (resolve, reject) => {
    const start = new Date()

    try {
      const outputPath = runId
        ? join(CONFIG.unligthouse_reports_dir, runId)
        : CONFIG.unligthouse_reports_dir

      ensureDir(outputPath)

      const unlighthouse = await createUnlighthouse(
        {
          site: site_url,
          outputPath,
          // NOTE: Do NOT set `urls` here if you want Unlighthouse to discover/crawl routes.
          // Setting `urls: [site_url]` effectively restricts scanning to a single page.
        },
        { name: 'cli' }
      )

      // Start the scan
      const { routes } = await unlighthouse.start()

      if (!routes.length) {
        return reject(new Error('Failed to queue routes for scanning'))
      }

      const { hooks, worker } = unlighthouse

      // Wait for scan completion
      hooks.hook('worker-finished', async () => {
        try {
          const end = new Date()
          const seconds = Math.round(
            (end.getTime() - start.getTime()) / 1000
          )

          const reports = worker.reports()
          const site_domain = new URL(site_url).hostname

          const results = await Promise.all(
            reports.map(async (routeReport) => {
              const fileName = `result.json`
              const domainDir = join(outputPath, site_domain)
              ensureDir(domainDir)
              const filePath = join(domainDir, fileName)

              console.log('Result written to : ',filePath);
              await writeFile(
                filePath,
                JSON.stringify(routeReport, null, 2),
                'utf-8'
              )

              return {
                url: routeReport.route.url,
                file: filePath
              }
            })
          )

          try {
            await worker.cluster.close()
          } catch (error) {
            if (
              !(error instanceof TypeError &&
                error.message.includes('display.close'))
            ) {
              console.error('Error closing cluster:', error)
            }
          }



          console.log('Process completed 1');
          resolve({
            success: true,
            scannedRoutes: routes.length,
            durationSeconds: seconds,
            reports: results
          })
        } catch (err) {
          reject(err)
        } 
      })
    } catch (err) {
      reject(err)
    }
  })
}

export default runUnlighthouse

// runUnlighthouse("http://127.0.0.1:5500/ui/index.html").then((result)=>{
//   console.log('completed 2');
//   // whyIsNodeRunning()
  
//   // ensure proper cleanup later
//   process.exit(0);
  
// }).catch((err)=>{
//   console.error(err)
//   process.exit(1);
// })
