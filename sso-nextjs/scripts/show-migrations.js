/**
 * Supabase 마이그레이션 출력 스크립트
 *
 * 각 마이그레이션 파일의 내용을 순서대로 출력합니다.
 * Supabase Dashboard SQL Editor에 복사-붙여넣기하세요.
 */

const fs = require('fs')
const path = require('path')

const migrationsDir = path.join(__dirname, '..', 'supabase', 'migrations')

// 마이그레이션 파일 목록 (순서대로)
const migrationFiles = fs.readdirSync(migrationsDir)
  .filter(file => file.endsWith('.sql'))
  .sort()

console.log('\n' + '='.repeat(70))
console.log('📋 SUPABASE MIGRATION FILES')
console.log('='.repeat(70))
console.log('\nℹ️  Instructions:')
console.log('   1. Open Supabase Dashboard: https://dqkghhlnnskjfwntdtor.supabase.co')
console.log('   2. Go to: SQL Editor → New Query')
console.log('   3. Copy each SQL below and run in order')
console.log('='.repeat(70))

migrationFiles.forEach((file, index) => {
  const filePath = path.join(migrationsDir, file)
  const content = fs.readFileSync(filePath, 'utf-8')

  console.log(`\n\n${'#'.repeat(70)}`)
  console.log(`# [${index + 1}/${migrationFiles.length}] ${file}`)
  console.log('#'.repeat(70))

  if (file.includes('drop_all')) {
    console.log('\n⚠️  WARNING: This will DELETE ALL DATA!')
    console.log('   Only run this if you want to reset the database completely.')
    console.log('\n--- Skip this file unless you need to reset ---\n')
  } else {
    console.log('\n--- Copy below SQL to Supabase Dashboard SQL Editor ---\n')
    console.log(content)
    console.log('\n--- End of SQL ---')
  }
})

console.log('\n\n' + '='.repeat(70))
console.log('✅ All migrations displayed.')
console.log('   Copy each SQL section to Supabase Dashboard and run.')
console.log('='.repeat(70))
console.log('')
