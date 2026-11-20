const data = {
 football: {
  matches: [
   ["Ligue des champions","🔴","Arsenal","🔵","Real Madrid","20:00"],
   ["Premier League","🔵","Manchester City","🔴","Liverpool","17:30"],
   ["Ligue 1","🔵","PSG","🟠","Marseille","21:00"]
  ],
  ranking: [["Arsenal","—"],["Manchester City","—"],["Liverpool","—"],["Chelsea","—"],["Tottenham","—"]]
 },
 basketball: {
  matches: [["NBA","🟣","Lakers","🟢","Celtics","02:00"],["NBA","🔴","Bulls","🟠","Heat","01:30"],["EuroLeague","⚫","Real Madrid","🟡","Fenerbahçe","19:00"]],
  ranking: [["Celtics","—"],["Lakers","—"],["Bulls","—"],["Heat","—"],["Warriors","—"]]
 },
 tennis: {
  matches: [["Tournoi","🎾","Joueur A","🎾","Joueur B","À venir"],["Tournoi","🎾","Joueur C","🎾","Joueur D","À venir"],["Tournoi","🎾","Joueur E","🎾","Joueur F","À venir"]],
  ranking: [["Joueur A","—"],["Joueur B","—"],["Joueur C","—"],["Joueur D","—"],["Joueur E","—"]]
 }
};
function render(sport){
 const d=data[sport];
 document.querySelector("#match-list").innerHTML=d.matches.map(m=>`<article class="match"><div class="league">${m[0]}</div><div class="teams"><div class="team"><span class="crest">${m[1]}</span>${m[2]}</div><span class="vs">VS</span><div class="team"><span class="crest">${m[3]}</span>${m[4]}</div></div><div class="match-foot"><span>◷ ${m[5]}</span><span>Programmation démo</span></div></article>`).join("");
 document.querySelector("#ranking").innerHTML=d.ranking.map((r,i)=>`<tr><td>${String(i+1).padStart(2,"0")}</td><td>${r[0]}</td><td>${r[1]}</td></tr>`).join("");
}
document.querySelectorAll(".tab").forEach(btn=>btn.addEventListener("click",()=>{
 document.querySelectorAll(".tab").forEach(b=>b.classList.remove("active"));
 btn.classList.add("active");render(btn.dataset.sport);
}));
render("football");
