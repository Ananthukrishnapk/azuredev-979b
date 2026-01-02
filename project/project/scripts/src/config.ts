import { z } from "zod"
import path from "path"
import { fileURLToPath } from 'url'

const __filename = fileURLToPath(import.meta.url)
const srcFolder = path.dirname(__filename)
const scriptsFloder = srcFolder + '/' + '../'
const projectDir = scriptsFloder + '../'

export const AppConfigSchema = z.object({
    paths: z.object({
        temp_dir: z.string(),
        unlighthouse_reports: z.string(),
        unlighthouse_artifacts: z.string(),
        projectDir: z.string().default(projectDir),
    }),

    execution: z.object({
        max_workers: z.number().int().positive(),
        timeout_sec: z.number().int().positive(),
    }).optional(),
})

export type AppConfig = z.infer<typeof AppConfigSchema>

export interface Config {
    temp_dir: string,
    unligthouse_reports_dir: string,
    projectDir: string
}

export function getConfig(config: AppConfig, project_dir: string): Config {

    return {
        temp_dir: path.join(project_dir, config.paths.temp_dir),
        unligthouse_reports_dir: path.join(
            project_dir,
            config.paths.temp_dir,
            config.paths.unlighthouse_reports
        ),
        projectDir: config.paths.projectDir
    }
}
