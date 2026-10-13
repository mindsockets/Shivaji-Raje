/* ============================================================
   Shivaji — A Story a Night · reading progress
   Remembers, in this browser only, which nights and saint stories
   have been opened and read. Nothing is sent anywhere.
   ============================================================ */
(function(){
  var KEY = "sasn.progress.v1";
  var NIGHTS = ["The Land That Waited","Birth at Shivneri","Jijabai's Lap","The Mavla Brotherhood","The Oath at Raireshwar",
    "The First Fort — Torna","Freeing Father Shahaji","Javali","The Giant Approaches","Pratapgad & Afzal Khan",
    "Panhala & Shiva Kashid","Pavan Khind & Baji Prabhu","Night Raid on the Lal Mahal","The Surat Raid","Purandar & Murarbaji",
    "Agra — The Cage & the Escape","Sinhagad & Tanaji","Salher","Nesari & Prataprao","Bahirji Naik & Ganimi Kava",
    "Raigad & Hirkani","The Coronation","Rajmata Jijabai Departs","Master of the Sea","The Southern Campaign",
    "The Just King","The Saints","The Last Days","The Dream That Didn't Die","The Memory Garland"];
  var ACT_STARTS = [1,7,13,17,24];
  var SAINTS = [["saint-varkari","The Road to Pandharpur"],["saint-tukaram","Sant Tukaram"],["saint-ramdas","Samarth Ramdas"],
    ["saint-mauni-baba","Mauni Baba"],["saint-sufi","Shared Faith"]];

  function pad(n){ return (n<10?"0":"")+n; }
  function dayId(n){ return "day-"+pad(n); }
  function load(){
    try { var d = JSON.parse(localStorage.getItem(KEY) || "null"); if (d && d.v===1) return d; } catch(e){}
    return {v:1, read:{}, seen:{}, last:null};
  }
  function save(d){ try { localStorage.setItem(KEY, JSON.stringify(d)); return true; } catch(e){ return false; } }
  var data = load();

  var path = location.pathname.split("/").pop() || "index.html";
  var page = path.replace(/\.html$/,"");
  var isNight = /^day-\d\d$/.test(page);
  var isSaint = /^saint-/.test(page);
  var nightNo = isNight ? parseInt(page.slice(4),10) : 0;

  function readNights(){ var c=0; for (var i=1;i<=30;i++) if (data.read[dayId(i)]) c++; return c; }
  function readSaints(){ return SAINTS.filter(function(s){ return data.read[s[0]]; }).length; }
  function nextUnreadFrom(n){ for (var i=n;i<=30;i++) if (!data.read[dayId(i)]) return i; for (i=1;i<n;i++) if (!data.read[dayId(i)]) return i; return 0; }
  function continueTarget(){
    var last = data.last && data.last.id;
    if (last && /^day-/.test(last)){
      var n = parseInt(last.slice(4),10);
      if (!data.read[last]) return n;
      return nextUnreadFrom(Math.min(n+1,30));
    }
    return nextUnreadFrom(1);
  }
  function when(ts){
    if (!ts) return "";
    var d = Math.floor((Date.now()-ts)/86400000);
    if (d<=0) return "today"; if (d===1) return "yesterday"; if (d<7) return d+" days ago";
    try { return "on "+new Date(ts).toLocaleDateString(undefined,{day:"numeric",month:"short"}); } catch(e){ return ""; }
  }
  function label(id){
    if (/^day-/.test(id)){ var n=parseInt(id.slice(4),10); return "Night "+n+" · "+NIGHTS[n-1]; }
    for (var i=0;i<SAINTS.length;i++) if (SAINTS[i][0]===id) return SAINTS[i][1];
    return id;
  }
  function esc(s){ return String(s).replace(/[&<>"]/g,function(c){return {"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c];}); }

  /* ---------- record a visit ---------- */
  if (isNight || isSaint){
    data.seen[page] = data.seen[page] || Date.now();
    data.last = {id:page, at:Date.now()};
    save(data);
  }

  function setRead(on){
    if (on) data.read[page] = Date.now(); else delete data.read[page];
    save(data); paint();
  }

  /* ---------- paint everything that shows progress ---------- */
  function paint(){
    var n = readNights(), pct = Math.round(n/30*100);
    // header chip
    Array.prototype.forEach.call(document.querySelectorAll(".sb-prog"), function(a){
      var ring = a.querySelector(".sb-ring"); if (ring) ring.style.setProperty("--p", pct);
      var t = a.querySelector("[data-sb-count]"); if (t) t.textContent = n ? (n+" / 30 read") : "My progress";
      a.title = n ? ("You have read "+n+" of 30 nights") : "Your reading progress";
    });
    // pager tick
    var pos = document.querySelector(".pager .pg-pos"); if (pos) pos.classList.toggle("is-read", !!data.read[page]);
    // mark-as-read box
    var rm = document.querySelector("[data-readmark]");
    if (rm){
      var name = isNight ? ("Night "+nightNo) : "this story";
      if (data.read[page]){
        var nx = isNight && nightNo<30 ? '<a class="rm-next" href="day-'+pad(nightNo+1)+'.html">Next: Night '+(nightNo+1)+' →</a>' : "";
        rm.className = "readmark is-read";
        rm.innerHTML = '<span class="rm-done">✓ '+esc(name)+' is marked as read</span>'+nx+'<button type="button" class="rm-undo" data-undo>undo</button>';
      } else {
        rm.className = "readmark";
        rm.innerHTML = '<button type="button" data-mark>✓ Mark '+esc(name)+' as read</button><span>Saved only in this browser.</span>';
      }
    }
    // home page
    var cont = document.querySelectorAll("[data-continue]");
    if (cont.length){
      var any = n || Object.keys(data.seen).length;
      var t = continueTarget();
      Array.prototype.forEach.call(cont, function(a){
        if (!any){ a.href = "day-01.html"; a.textContent = "▶ Begin — Night 1"; }
        else if (t){ a.href = "day-"+pad(t)+".html"; a.textContent = "▶ Continue — Night "+t+": "+NIGHTS[t-1]; }
        else { a.href = "saints.html"; a.textContent = "✓ All 30 read — try the saints"; }
      });
    }
    var cnt = document.querySelector("[data-count]");
    if (cnt) cnt.textContent = n ? (n+" of 30 nights read") : "30 nights · about 10 minutes each";
    Array.prototype.forEach.call(document.querySelectorAll("a.night[href^='day-']"), function(a){
      var id = a.getAttribute("href").replace(/\.html$/,""), s = a.querySelector(".s");
      a.classList.toggle("is-read", !!data.read[id]);
      if (s){
        if (!s.hasAttribute("data-orig")) s.setAttribute("data-orig", s.textContent);
        s.classList.toggle("read", !!data.read[id]);
        s.textContent = data.read[id] ? "✓ Read" : (data.seen[id] ? "Started" : s.getAttribute("data-orig"));
      }
    });
    Array.prototype.forEach.call(document.querySelectorAll("a.saint-card"), function(a){
      var id = a.getAttribute("href").replace(/\.html$/,""), nm = a.querySelector(".nm"); if (!nm) return;
      var b = nm.querySelector(".read-badge");
      if (data.read[id] && !b){ b = document.createElement("span"); b.className="read-badge"; b.textContent="✓ read"; nm.appendChild(b); }
      if (!data.read[id] && b) b.remove();
    });
    var panel = document.getElementById("progress-panel");
    if (panel) panel.innerHTML = panelHtml(n);
    Array.prototype.forEach.call(document.querySelectorAll("[data-foot-progress]"), function(el){
      var last = data.last ? ('Last opened: <a href="'+data.last.id+'.html">'+esc(label(data.last.id))+'</a> ('+when(data.last.at)+').') : "Nothing read yet.";
      el.innerHTML = '<p>'+n+' of 30 nights and '+readSaints()+' of 5 saint stories read. '+last+'</p><p>Saved only in this browser on this device.</p>';
    });
  }

  function panelHtml(n){
    var beads = "", t = continueTarget();
    for (var i=1;i<=30;i++){
      var id = dayId(i), cls = data.read[id] ? "read" : (data.seen[id] ? "seen" : "");
      if (ACT_STARTS.indexOf(i)>0) cls += " act-start";
      beads += '<a class="'+cls+'" href="'+id+'.html" title="Night '+i+' · '+esc(NIGHTS[i-1])+(data.read[id]?" · read":(data.seen[id]?" · started":""))+'" aria-label="Night '+i+(data.read[id]?", read":"")+'"></a>';
    }
    var lastLine = data.last ? ('Last opened <a href="'+data.last.id+'.html">'+esc(label(data.last.id))+'</a> '+when(data.last.at)+'.') : "Open any night to begin. A night is marked read when you reach its goodnight line, or with the ✓ button under the story.";
    var btn = !n && !Object.keys(data.seen).length ? '<a class="btn" href="day-01.html">▶ Begin — Night 1</a>'
            : (t ? '<a class="btn" href="day-'+pad(t)+'.html">▶ Continue — Night '+t+': '+esc(NIGHTS[t-1])+'</a>'
                 : '<a class="btn" href="saints.html">✓ All 30 read — now the saints</a>');
    return '<div class="pp-top"><h2>Your progress</h2><span class="pp-count"><b>'+n+'</b> of 30 nights · <b>'+readSaints()+'</b> of 5 saint stories</span></div>'+
      '<div class="pp-beads">'+beads+'</div>'+
      '<div class="pp-acts" aria-hidden="true"><span>Act I</span><span>Act II</span><span>Act III</span><span>Act IV</span><span>Act V</span></div>'+
      '<div class="pp-row">'+btn+'<span class="pp-count">'+lastLine+'</span></div>'+
      '<p class="pp-note">Saved only in this browser on this device; nothing is sent anywhere. Filled bead = read, ringed bead = started.</p>';
  }

  /* ---------- events ---------- */
  var undone = false;
  document.addEventListener("click", function(e){
    if (e.target.closest("[data-mark]")) { setRead(true); }
    else if (e.target.closest("[data-undo]")) { undone = true; setRead(false); }
    else if (e.target.closest("[data-reset]")) {
      if (window.confirm("Clear all reading progress saved in this browser?")) {
        data = {v:1, read:{}, seen:{}, last:null}; save(data); paint();
      }
    }
  });

  /* auto-mark: reaching the goodnight line of the story counts as reading it */
  if ((isNight || isSaint) && "IntersectionObserver" in window){
    var io = new IntersectionObserver(function(entries){
      entries.forEach(function(en){
        if (en.isIntersecting && en.target.offsetParent !== null && !undone && !data.read[page]) setRead(true);
      });
    }, {threshold:0.6});
    Array.prototype.forEach.call(document.querySelectorAll(".goodnight"), function(g){ io.observe(g); });
  }

  paint();
})();
