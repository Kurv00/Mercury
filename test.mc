<var>
x: 10;
y: 3;
msg: "This is Mercury!";
msg2: "yrucreM";
</var>

<print>{msg}</print>
<calc>x * y + 5</calc>

<if condition="x > y">
  <print>{x} is greater than {y}</print>
</if>

<for var="i" in="(1, 5)">
  <print>Value: {i}</print>
</for>

<rprint>{msg2}</rprint>
