import fs from "fs"
import path from "path"

export function ensureDir(dir: string) {
    fs.mkdirSync(dir, { recursive: true })
}
