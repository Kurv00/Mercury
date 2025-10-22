<var>
x: 10;
y: 3;
msg: "This is Mercury!";
msg2: "!enoD llA";
</var>

<print>{msg}</print>
<calc>x * y + 5</calc>

<if condition="x > y">
  <print>{x} is greater than {y}</print>
</if>

<for var="i" range="(1, 5)">
  <print>Value Number: {i}</print>
</for>

<wait seconds="1"/>
<print>This text appeared 1 second later</print>

<wait seconds="2"/>
<print>This test appeared 2 second later</print>

<rprint>{msg2}</rprint>