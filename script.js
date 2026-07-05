// Contact obfuscation — prevents bots from scraping phone/email/reg numbers
(function() {
    var p = [57,52,49,57,49,57,48,51,56,56].map(function(c){return String.fromCharCode(c)}).join('');
    var e = [97,110,105,108,55,100,104,97,114,64,103,109,97,105,108,46,99,111,109].map(function(c){return String.fromCharCode(c)}).join('');
    var r = [51,54,55,50].map(function(c){return String.fromCharCode(c)}).join('');
    var r2 = [53,55,55,53].map(function(c){return String.fromCharCode(c)}).join('');
    var r3 = [53,55,56,52].map(function(c){return String.fromCharCode(c)}).join('');
    var pf = p.slice(0,5) + ' ' + p.slice(5);
    var msg = encodeURIComponent('Dr. Dhar I would like to book an appointment\n\nName: \nAge: \nDate: \nTime: ');
    document.querySelectorAll('[data-obf="phone"]').forEach(function(el){el.textContent=pf});
    document.querySelectorAll('[data-obf="email"]').forEach(function(el){el.textContent=e});
    document.querySelectorAll('[data-obf="reg"]').forEach(function(el){el.textContent='MBBS: '+r+' · MD: '+r2+' · DNB: '+r3});
    document.querySelectorAll('[data-obf-href="tel"]').forEach(function(el){el.href='tel:+91'+p});
    document.querySelectorAll('[data-obf-href="wa"]').forEach(function(el){el.href='https://wa.me/91'+p+'?text='+msg});
    document.querySelectorAll('[data-obf-href="sms"]').forEach(function(el){el.href='sms:+91'+p+'?body='+msg});
    document.querySelectorAll('[data-obf-href="email"]').forEach(function(el){el.href='mailto:'+e});
})();

function updateClinicStatus() {
    const statusBadge = document.getElementById('clinic-status');
    const statusDot = statusBadge.querySelector('.status-dot');
    const statusText = statusBadge.querySelector('.status-text');
    const now = new Date();
    const istTime = new Date(now.toLocaleString("en-US", {timeZone: "Asia/Kolkata"}));
    const day = istTime.getDay();
    const hours = istTime.getHours();
    const minutes = istTime.getMinutes();
    const currentTime = hours * 60 + minutes;
    const schedule = {
        1: [{ start: 540, end: 780 }, { start: 990, end: 1140 }],
        2: [],
        3: [{ start: 540, end: 780 }, { start: 990, end: 1140 }],
        4: [{ start: 540, end: 780 }, { start: 990, end: 1140 }],
        5: [{ start: 540, end: 780 }, { start: 990, end: 1140 }],
        6: [{ start: 540, end: 780 }, { start: 990, end: 1140 }],
        0: [{ start: 540, end: 900 }]
    };
    let isOpen = false;
    const todaySchedule = schedule[day] || [];
    for (const slot of todaySchedule) {
        if (currentTime >= slot.start && currentTime < slot.end) { isOpen = true; break; }
    }
    function formatTime12Hour(totalMinutes) {
        const h = Math.floor(totalMinutes / 60);
        const m = totalMinutes % 60;
        const period = h >= 12 ? 'PM' : 'AM';
        const dh = h > 12 ? h - 12 : (h === 0 ? 12 : h);
        return `${dh}:${m.toString().padStart(2, '0')} ${period}`;
    }
    if (isOpen) {
        statusBadge.classList.add('open');
        statusBadge.classList.remove('closed');
        statusText.textContent = 'Open Now';
    } else {
        statusBadge.classList.add('closed');
        statusBadge.classList.remove('open');
        let nextOpen = '';
        let foundToday = false;
        for (const slot of todaySchedule) {
            if (currentTime < slot.start) { nextOpen = `Opens at ${formatTime12Hour(slot.start)}`; foundToday = true; break; }
        }
        if (!foundToday) {
            const tomorrow = (day + 1) % 7;
            const ts = schedule[tomorrow] || [];
            if (ts.length === 0) {
                const da = (tomorrow + 1) % 7;
                const das = schedule[da] || [];
                if (das.length > 0) {
                    const dn = ['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday'];
                    nextOpen = `Opens ${dn[da]} at ${formatTime12Hour(das[0].start)}`;
                }
            } else { nextOpen = `Opens tomorrow at ${formatTime12Hour(ts[0].start)}`; }
        }
        statusText.textContent = `Closed • ${nextOpen}`;
    }
}
updateClinicStatus();
setInterval(updateClinicStatus, 60000);

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => { if (entry.isIntersecting) entry.target.classList.add('visible'); });
}, { threshold: 0.1, rootMargin: '0px 0px -50px 0px' });

document.querySelectorAll('section').forEach(s => { s.classList.add('fade-in-section'); observer.observe(s); });
document.querySelectorAll('.services-grid, .contact-grid').forEach(g => observer.observe(g));

const btt = document.getElementById('back-to-top');
window.addEventListener('scroll', () => { btt.classList.toggle('visible', window.pageYOffset > 300); });
btt.addEventListener('click', () => window.scrollTo({ top: 0, behavior: 'smooth' }));
